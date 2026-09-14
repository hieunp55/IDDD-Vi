```java
private Set<Sprint> sprints;
private TenantId tenantId;
...
}

```

Mô hình Aggregate (cụm tập hợp các thực thể và đối tượng giá trị có cùng ranh giới nhất quán) kích thước lớn thoạt nhìn có vẻ rất hấp dẫn, nhưng trên thực tế lại không hề khả thi. Khi ứng dụng đi vào vận hành trong môi trường đa người dùng (multi-user) thực tế, nó bắt đầu liên tục gặp phải các lỗi thất bại giao dịch (transactional failure). Hãy cùng xem xét kỹ hơn một vài mẫu hình sử dụng của client (phía gọi dịch vụ) và cách chúng tương tác với mô hình giải pháp kỹ thuật của chúng ta. Các instance (thực thể thể hiện) của Aggregate sử dụng cơ chế optimistic concurrency (kiểm soát đồng thời lạc quan) nhằm bảo vệ các persistent object (đối tượng lưu trữ bền vững) khỏi các thao tác chỉnh sửa trùng lặp diễn ra đồng thời từ nhiều client khác nhau, qua đó tránh việc phải sử dụng database lock (khóa cơ sở dữ liệu). Như đã thảo luận trong chương Entities (5), các đối tượng mang theo một số phiên bản (version number); số này sẽ tự động tăng lên mỗi khi có thay đổi và được kiểm tra trước khi lưu xuống cơ sở dữ liệu. Nếu số phiên bản trên đối tượng đã lưu trong cơ sở dữ liệu lớn hơn số phiên bản trên bản sao của client, bản sao của client sẽ bị coi là lỗi thời (stale) và yêu cầu cập nhật sẽ bị từ chối.

Hãy xem xét một kịch bản sử dụng đồng thời thường gặp với nhiều client:

* Hai người dùng, Bill và Joe, cùng xem một Product (sản phẩm) mang phiên bản 1 và bắt đầu thao tác trên đó.
* Bill lên kế hoạch cho một BacklogItem (hạng mục công việc tồn đọng) mới và commit (ghi nhận giao dịch). Phiên bản của Product được tăng lên thành 2.
* Joe lên lịch cho một Release (bản phát hành) mới và cố gắng lưu lại, nhưng commit của anh ấy thất bại vì thao tác đó dựa trên Product phiên bản 1.

Các cơ chế lưu trữ (persistence mechanism) thường được sử dụng theo cách tổng quát này để xử lý vấn đề tranh chấp đồng thời. 1 Nếu bạn lập luận rằng cấu hình đồng thời mặc định có thể thay đổi được, xin hãy tạm hoãn đưa ra phán quyết thêm một chút. Cách tiếp cận này thực chất đóng vai trò rất quan trọng trong việc bảo vệ các invariant (bất biến - các quy tắc nghiệp vụ luôn phải được đảm bảo đúng) của Aggregate trước những thay đổi đồng thời.

Hình 10.1 Product được mô hình hóa dưới dạng một Aggregate kích thước rất lớn

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000381_ae8579f2a1111e995514297ae1a650737b1068bfa0f846747666c69798d809e8.png)

1. Chẳng hạn, Hibernate cung cấp cơ chế kiểm soát đồng thời lạc quan theo cách này. Điều tương tự cũng có thể đúng với một kho lưu trữ dạng key-value, bởi vì toàn bộ Aggregate thường được tuần tự hóa (serialize) thành một giá trị duy nhất, trừ khi được thiết kế để lưu riêng từng phần cấu thành.

Hình 10.2 Product và các khái niệm liên quan được mô hình hóa thành các kiểu Aggregate riêng biệt.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000382_7a79ea50bb7eeca7b7dae1c7ec94c037d1efeb9267c18bd614d6d7cc84b49f8d.png)

Các vấn đề về tính nhất quán này xuất hiện chỉ với hai người dùng. Nếu có thêm nhiều người dùng hơn, bạn sẽ đối mặt với một vấn đề thực sự nghiêm trọng. Với Scrum (khung làm việc phát triển linh hoạt), nhiều người dùng thường xuyên thực hiện các thao tác sửa đổi chồng chéo như vậy trong suốt phiên họp sprint planning (lập kế hoạch sprint - chu kỳ phát triển lặp ngắn) và quá trình thực thi sprint. Việc liên tục từ chối tất cả các yêu cầu ngoại trừ một yêu cầu duy nhất là điều hoàn toàn không thể chấp nhận được.

Về mặt logic, việc lập kế hoạch cho một backlog item mới chẳng có lý do gì lại can thiệp hay cản trở việc lên lịch cho một release mới! Vậy tại sao commit của Joe lại thất bại? Cốt lõi của vấn đề nằm ở chỗ: Aggregate dạng cụm lớn (large-cluster Aggregate) đã được thiết kế dựa trên các "bất biến giả" (false invariant) chứ không phải các quy tắc nghiệp vụ thực sự. Những bất biến giả này là các ràng buộc nhân tạo do chính các lập trình viên tự áp đặt lên hệ thống. Đội ngũ phát triển hoàn toàn có những cách khác để ngăn chặn việc xóa dữ liệu không hợp lệ mà không cần phải áp đặt các giới hạn độc đoán như vậy. Ngoài việc gây ra các sự cố giao dịch, thiết kế này còn kéo theo những nhược điểm nghiêm trọng về hiệu năng và khả năng mở rộng (scalability).

## Lần thử thứ hai: Nhiều Aggregate riêng biệt

Bây giờ hãy xem xét một mô hình thay thế như minh họa trong Hình 10.2, nơi có bốn Aggregate riêng biệt. Mỗi quan hệ phụ thuộc được liên kết thông qua suy luận (association by inference) bằng cách sử dụng chung một ProductId (mã định danh sản phẩm) — danh tính của Product vốn được xem là cha của ba Aggregate còn lại.

Việc chia nhỏ một Aggregate đơn lẻ kích thước lớn thành bốn Aggregate sẽ làm thay đổi một số giao ước phương thức (method contract) trên Product. Với thiết kế Aggregate dạng cụm lớn ban đầu, chữ ký phương thức trông như sau:

```java
    BacklogItemType aType,
    StoryPoints aStoryPoints) {

```

```java
public class Product ... {
    ...
    public void planBacklogItem(
        String aSummary,
        String aCategory,
        ...
    }
    ...
    public void scheduleRelease(
        String aName,
        String aDescription,

```

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000383_852bbaa50e8db77a5b875f52b0ef136c7ed9ee36b74c3ffc71c43f2ff0d95e7a.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000384_54e6d51b092db67d246b69fd2b98d5a835aae8e1e44d4b68c2e726d95e44de47.png)

## Chương 10: AGGREGATE

```java
        Date aBegins,
        Date anEnds) {
        ...
    }

    public void scheduleSprint(
        String aName,
        String aGoals,
        Date aBegins,
        Date anEnds) {
        ...
    }
    ...
}

```

Tất cả các phương thức này đều là command (lệnh) theo nguyên lý CQS (Command-Query Separation - nguyên tắc phân tách lệnh và truy vấn) [Fowler, CQS]; nghĩa là chúng làm thay đổi trạng thái của Product bằng cách thêm phần tử mới vào một collection (tập hợp), do đó chúng có kiểu trả về là `void`. Tuy nhiên, với thiết kế gồm nhiều Aggregate, chúng ta có:

```java
public class Product ... {
    ...
    public BacklogItem planBacklogItem(
        String aSummary,
        String aCategory,
        BacklogItemType aType,
        StoryPoints aStoryPoints) {
        ...
    }

    public Release scheduleRelease(
        String aName,
        String aDescription,
        Date aBegins,
        Date anEnds) {
        ...
    }

    public Sprint scheduleSprint(
        String aName,
        String aGoals,
        Date aBegins,
        Date anEnds) {
        ...
    }
    ...
}

```

Các phương thức được tái thiết kế này tuân theo giao ước truy vấn của CQS và đóng vai trò như các Factory (11) (mẫu thiết kế nhà máy tạo lập đối tượng); tức là mỗi phương thức sẽ tạo ra một instance của Aggregate mới và trả về tham chiếu đến nó. Giờ đây, khi một client muốn lên kế hoạch cho một backlog item, Application Service (14) (dịch vụ ứng dụng) có quản lý giao dịch phải thực hiện như sau:

```java
public class ProductBacklogItemService ... {
    ...
    @Transactional
    public void planProductBacklogItem(

```

```java
        String aTenantId,
        String aProductId,
        String aSummary,
        String aCategory,
        String aBacklogItemType,
        String aStoryPoints) {

    Product product =
        productRepository.productOfId(
            new TenantId(aTenantId),
            new ProductId(aProductId));

    BacklogItem plannedBacklogItem =
        product.planBacklogItem(
            aSummary,
            aCategory,
            BacklogItemType.valueOf(aBacklogItemType),
            StoryPoints.valueOf(aStoryPoints));

    backlogItemRepository.add(plannedBacklogItem);
}
...
}

```

Như vậy, chúng ta đã giải quyết triệt để sự cố thất bại giao dịch bằng cách tái cấu trúc mô hình để loại bỏ nó hoàn toàn (modeling it away). Giờ đây, bất kỳ số lượng instance nào của `BacklogItem`, `Release` và `Sprint` đều có thể được tạo ra một cách an toàn trước các yêu cầu đồng thời từ người dùng. Mọi thứ trở nên khá đơn giản.

Tuy nhiên, ngay cả khi sở hữu những ưu thế giao dịch rõ rệt, bốn Aggregate nhỏ hơn này lại kém thuận tiện hơn dưới góc nhìn sử dụng của phía client. Liệu thay vào đó, chúng ta có thể tinh chỉnh Aggregate lớn để loại bỏ các vấn đề tranh chấp đồng thời hay không? Bằng cách thiết lập tùy chọn `optimistic-lock` trong ánh xạ Hibernate thành `false`, chúng ta sẽ dập tắt được hiệu ứng domino gây thất bại giao dịch. Do không có bất kỳ quy tắc invariant nào ràng buộc tổng số lượng các instance `BacklogItem`, `Release` hay `Sprint` được tạo ra, vậy tại sao không để các collection này phát triển không giới hạn và bỏ qua các chỉnh sửa cụ thể này trên `Product`? Cái giá phải trả thêm khi giữ lại Aggregate dạng cụm lớn là gì? Vấn đề là kích thước của nó có thể thực sự phình to vượt tầm kiểm soát. Trước khi phân tích kỹ lưỡng lý do tại sao, hãy cùng xem xét lời khuyên mô hình hóa quan trọng nhất mà đội ngũ SaaSOvation cần có.

## Quy tắc: Mô hình hóa các bất biến thực sự trong ranh giới nhất quán

Khi tìm cách xác định các Aggregate trong một Bounded Context (2) (ngữ cảnh giới hạn - ranh giới phân định mô hình nghiệp vụ), chúng ta phải hiểu rõ các invariant thực sự của mô hình. Chỉ khi nắm vững kiến thức đó, chúng ta mới có thể xác định chính xác những đối tượng nào nên được gom cụm vào một Aggregate nhất định.

Một invariant là một quy tắc nghiệp vụ luôn luôn phải được đảm bảo nhất quán. Có nhiều loại nhất quán khác nhau. Một là transactional consistency (tính nhất quán cấp giao dịch), vốn được coi là mang tính tức thời và nguyên tử (atomic). Ngoài ra còn có eventual consistency (tính nhất quán sau cùng / nhất quán cuối cùng). Khi bàn về các invariant, chúng ta đang đề cập đến tính nhất quán cấp giao dịch. Giả sử chúng ta có quy tắc invariant sau:

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000385_9876f6e57d60f93c539bf944d4d32362b0407e5e6f41bff84f45ed2494bac713.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000386_4e83569f8648925e7a926977a6ab922e5b24517bd43865f42663424d67baa06f.png)

```
c = a + b

```

Do đó, khi a là 2 và b là 3, c bắt buộc phải là 5. Theo quy tắc và các điều kiện đó, nếu c là bất kỳ giá trị nào khác 5, một invariant của hệ thống đã bị vi phạm. Để đảm bảo c luôn nhất quán, chúng ta thiết kế một ranh giới bao quanh các thuộc tính cụ thể này của mô hình:

```java
AggregateType1 {
    int a;
    int b;
    int c;
    operations ...
}

```

Ranh giới nhất quán khẳng định về mặt logic rằng mọi thứ bên trong nó đều phải tuân thủ một tập hợp các quy tắc bất biến nghiệp vụ cụ thể, bất kể thao tác nào được thực hiện. Tính nhất quán của mọi thứ nằm ngoài ranh giới này không liên quan đến Aggregate. Do đó, Aggregate đồng nghĩa với ranh giới nhất quán giao dịch (transactional consistency boundary). (Trong ví dụ giới hạn này, `AggregateType1` có ba thuộc tính kiểu `int`, nhưng bất kỳ Aggregate cụ thể nào cũng có thể chứa các thuộc tính thuộc nhiều kiểu khác nhau.)

Khi sử dụng một cơ chế lưu trữ điển hình, chúng ta dùng một giao dịch duy nhất 2 để quản lý tính nhất quán. Khi giao dịch được commit, mọi thứ bên trong một ranh giới phải đạt trạng thái nhất quán. Một Aggregate được thiết kế đúng đắn là Aggregate có thể được sửa đổi theo bất kỳ cách nào mà nghiệp vụ yêu cầu, trong khi các invariant của nó vẫn hoàn toàn nhất quán trong phạm vi một giao dịch duy nhất. Và một Bounded Context được thiết kế chuẩn mực sẽ chỉ sửa đổi duy nhất một instance của Aggregate trên mỗi giao dịch trong mọi trường hợp. Hơn thế nữa, chúng ta không thể lập luận chuẩn xác về thiết kế Aggregate nếu không áp dụng phân tích giao dịch (transactional analysis).

Việc giới hạn chỉ sửa đổi một instance của Aggregate trong mỗi giao dịch nghe có vẻ quá nghiêm ngặt. Tuy nhiên, đó là một nguyên tắc kinh nghiệm (rule of thumb) và nên là mục tiêu hướng tới trong hầu hết các trường hợp. Nó giải quyết đúng lý do cốt lõi của việc sử dụng Aggregate.

2. Giao dịch này có thể được quản lý bởi một Unit of Work (mẫu đơn vị công việc) [Fowler, P of EAA].

## Giờ thực hành trên bảng trắng

* Liệt kê lên bảng trắng tất cả các Aggregate dạng cụm lớn trong hệ thống của bạn.
* Ghi chú bên cạnh mỗi Aggregate lý do tại sao nó là một cụm lớn và bất kỳ vấn đề tiềm ẩn nào do kích thước của nó gây ra.
* Bên cạnh danh sách đó, hãy gọi tên bất kỳ Aggregate nào đang bị sửa đổi cùng nhau trong cùng một giao dịch với các Aggregate khác.
* Ghi chú bên cạnh mỗi Aggregate đó xem liệu bất biến thực sự (true invariant) hay bất biến giả (false invariant) đã dẫn đến việc hình thành các ranh giới Aggregate được thiết kế kém này.

Việc các Aggregate bắt buộc phải được thiết kế tập trung vào tính nhất quán ngụ ý rằng giao diện người dùng nên thu hẹp phạm vi của từng yêu cầu nhằm chỉ thực thi một command duy nhất trên đúng một instance của Aggregate. Nếu các yêu cầu từ người dùng cố gắng hoàn thành quá nhiều việc cùng lúc, ứng dụng sẽ bị buộc phải sửa đổi nhiều instance cùng một thời điểm.

Vì vậy, bản chất cốt lõi của Aggregate là xoay quanh các ranh giới nhất quán chứ không xuất phát từ mong muốn thiết kế các đồ thị đối tượng (object graph). Một số invariant ngoài đời thực sẽ phức tạp hơn thế này. Dẫu vậy, các invariant thông thường sẽ ít đòi hỏi nỗ lực mô hình hóa hơn, từ đó mở ra khả năng thiết kế các Aggregate kích thước nhỏ.

## Quy tắc: Thiết kế các Aggregate kích thước nhỏ

Giờ đây chúng ta có thể giải quyết thấu đáo câu hỏi này: Cái giá phải trả thêm khi giữ lại Aggregate dạng cụm lớn là gì? Ngay cả khi chúng ta đảm bảo rằng mọi giao dịch đều sẽ thành công, một cụm lớn vẫn hạn chế đáng kể hiệu năng và khả năng mở rộng. Khi SaaSOvation phát triển thị trường, nó sẽ thu hút một lượng lớn tenant (khách hàng thuê bao / tổ chức sử dụng). Khi mỗi tenant gắn bó sâu rộng với ProjectOvation, SaaSOvation sẽ lưu trữ ngày càng nhiều dự án cùng các tài liệu quản lý (artifact) đi kèm. Điều đó sẽ dẫn đến số lượng khổng lồ các product, backlog item, release, sprint và nhiều thành phần khác. Hiệu năng và khả năng mở rộng là những yêu cầu phi chức năng (nonfunctional requirements) không thể xem nhẹ.

Đặt hiệu năng và khả năng mở rộng lên hàng đầu, điều gì sẽ xảy ra khi một người dùng thuộc một tenant muốn thêm một backlog item đơn lẻ vào một product đã tồn tại nhiều năm và có sẵn hàng nghìn backlog item? Giả sử cơ chế lưu trữ có khả năng lazy loading (nạp lười / trì hoãn nạp dữ liệu) như Hibernate. Chúng ta gần như không bao giờ nạp toàn bộ các backlog item, release và sprint cùng một lúc. Thế nhưng, hàng nghìn backlog item vẫn sẽ bị nạp vào bộ nhớ chỉ để thêm một phần tử mới vào collection vốn đã rất lớn. Tình hình sẽ tồi tệ hơn nhiều nếu cơ chế lưu trữ không hỗ trợ lazy loading. Thậm chí dù đã lưu tâm đến vấn đề bộ nhớ, đôi khi chúng ta vẫn buộc phải nạp nhiều collection cùng lúc, chẳng hạn như khi xếp lịch một backlog item vào release hoặc gán nó vào sprint; khi đó toàn bộ backlog item, và hoặc là toàn bộ release hoặc toàn bộ sprint, đều sẽ bị nạp vào bộ nhớ.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000387_5cda185f6718b1cc7653facb9b1af60c18b0d830ed3b086c4cb2aca143c61d29.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000388_eccdd0f99f8173d117fab5d39e6e229d54a0556d26900f2474084fcf85076c1b.png)

Để thấy rõ điều này, hãy nhìn vào sơ đồ ở Hình 10.3 chứa phần cấu thành được phóng to. Đừng để con số biểu thị quan hệ `0..*` đánh lừa bạn; số lượng các liên kết hầu như không bao giờ bằng 0 và sẽ liên tục tăng dần theo thời gian. Chúng ta rất có thể sẽ phải nạp hàng nghìn, hàng vạn đối tượng vào bộ nhớ cùng một lúc chỉ để thực hiện một thao tác lẽ ra là tương đối cơ bản. Đó mới chỉ tính cho một thành viên duy nhất thuộc một tenant duy nhất trên một product duy nhất. Chúng ta phải luôn nhớ rằng tình huống này có thể diễn ra đồng thời với hàng trăm hoặc hàng nghìn tenant, mỗi tenant lại có nhiều đội ngũ và nhiều product. Và theo thời gian, tình trạng này sẽ chỉ ngày một trầm trọng hơn.

Aggregate dạng cụm lớn này sẽ không bao giờ đạt được hiệu năng tốt hay mở rộng hiệu quả. Nó nhiều khả năng sẽ trở thành một cơn ác mộng chỉ dẫn đến thất bại. Nó đã khiếm khuyết ngay từ đầu bởi vì chính các bất biến giả cùng mong muốn thuận tiện trong cấu thành đối tượng đã định hình nên thiết kế, gây tổn hại trực tiếp đến tỷ lệ thành công của giao dịch, hiệu năng và khả năng mở rộng.

Nếu chúng ta dự định thiết kế các Aggregate nhỏ, thì từ "nhỏ" ở đây có nghĩa là gì? Trường hợp cực đoan nhất là một Aggregate chỉ có định danh duy nhất toàn cục và một thuộc tính bổ sung — đây không phải là điều được khuyến khích (trừ khi đó thực sự là những gì mà một Aggregate cụ thể đòi hỏi). Thay vào đó, hãy giới hạn Aggregate chỉ gồm Root Entity (thực thể gốc) cùng một số lượng tối thiểu các thuộc tính hoặc các thuộc tính có kiểu Value Object (đối tượng giá trị). 3 Mức tối thiểu chuẩn xác là đúng bằng những gì thực sự cần thiết, không thừa không thiếu.

Hình 10.3 Với mô hình Product này, nhiều collection lớn bị nạp vào bộ nhớ trong quá trình thực hiện nhiều thao tác cơ bản.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000389_007bf73e92a97a1c697d83dbc1ac8665b268663497bffe4bfe5ca498ca110a6c.png)

Những thuộc tính nào là cần thiết? Câu trả lời đơn giản là: những thuộc tính bắt buộc phải nhất quán với nhau, ngay cả khi các domain expert (chuyên gia nghiệp vụ) không nêu rõ chúng dưới dạng các quy tắc. Ví dụ, `Product` có các thuộc tính `name` (tên) và `description` (mô tả). Chúng ta không thể tưởng tượng được việc `name` và `description` lại không nhất quán với nhau khi bị mô hình hóa thành các Aggregate riêng biệt. Khi bạn thay đổi `name`, nhiều khả năng bạn cũng sẽ thay đổi `description`. Nếu bạn chỉ thay đổi một thuộc tính mà không thay đổi thuộc tính kia, có thể là do bạn đang sửa một lỗi chính tả hoặc điều chỉnh lại phần mô tả sao cho phù hợp hơn với tên gọi. Mặc dù các chuyên gia nghiệp vụ có thể không coi đây là một quy tắc nghiệp vụ tường minh, nhưng nó là một quy tắc ngầm định.

Nếu bạn nghĩ rằng mình nên mô hình hóa một phần thành phần bên trong thành một Entity thì sao? Trước tiên, hãy tự hỏi liệu phần thành phần đó có tự thay đổi theo thời gian hay không, hay nó có thể được thay thế hoàn toàn mỗi khi có sự thay đổi. Các trường hợp mà các instance có thể được thay thế hoàn toàn đều hướng tới việc sử dụng một Value Object thay vì một Entity. Đôi khi các phần cấu thành dạng Entity là cần thiết. Tuy nhiên, nếu chúng ta rà soát lại bài toán thiết kế này theo từng trường hợp cụ thể, nhiều khái niệm vốn đang được mô hình hóa dưới dạng Entity hoàn toàn có thể được tái cấu trúc thành Value Object. Việc ưu tiên các kiểu Value Object làm thành phần cấu thành Aggregate không có nghĩa là Aggregate đó mang tính bất biến (immutable), bởi vì bản thân Root Entity vẫn biến đổi trạng thái khi một trong các thuộc tính kiểu Value Object của nó được thay thế bằng giá trị mới.

Có những lợi thế rất quan trọng khi giới hạn các phần cấu thành bên trong ở dạng Value Object. Tùy thuộc vào cơ chế lưu trữ của bạn, các Value Object có thể được tuần tự hóa cùng với Root Entity, trong khi các Entity có thể đòi hỏi vùng lưu trữ được theo dõi độc lập. Chi phí phụ trội (overhead) sẽ cao hơn nhiều đối với các thành phần kiểu Entity, chẳng hạn như khi bắt buộc phải dùng các phép SQL join để đọc dữ liệu của chúng qua Hibernate. Việc chỉ đọc một dòng duy nhất trong bảng cơ sở dữ liệu sẽ nhanh hơn rất nhiều. Các Value Object có kích thước nhỏ hơn và an toàn hơn khi sử dụng (ít lỗi hơn). Nhờ tính bất biến, các unit test (kiểm thử đơn vị) cũng dễ dàng chứng minh tính chính xác của chúng hơn. Những ưu thế này đã được thảo luận trong chương Value Objects (6).

Trong một dự án thuộc lĩnh vực công cụ tài chính phái sinh sử dụng Qi4j [Öberg], Niclas Hedhman 4 đã báo cáo rằng đội ngũ của ông có thể thiết kế khoảng 70% tổng số Aggregate chỉ gồm một Root Entity duy nhất chứa một số thuộc tính kiểu Value Object. 30% còn lại chỉ có tổng cộng từ hai đến ba Entity. Điều này không có nghĩa là mọi mô hình miền đều sẽ có tỷ lệ phân chia 70/30. Nó chỉ ra rằng một tỷ lệ rất cao các Aggregate hoàn toàn có thể được giới hạn trong một Entity duy nhất: chính là Aggregate Root.

3. Thuộc tính có kiểu Value Object là thuộc tính nắm giữ một tham chiếu đến một Value Object. Tôi phân biệt điều này với một thuộc tính đơn giản như kiểu chuỗi hay kiểu số, tương tự như cách Ward Cunningham mô tả về Whole Value (mẫu giá trị hoàn chỉnh) [Cunningham, Whole Value].
4. Xem thêm tại www.jroller.com/niclas/

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000390_535f82a381a980b509aa6320abbd4ab09754d85ea3f63798e0632b1a03e8e66b.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000391_bbc584492205d0a1b22d161e8893d530c27ac50017bbe1aabed3402834dffbc1.png)

Phần thảo luận về Aggregate của [Evans] đã đưa ra một ví dụ cho thấy việc có nhiều Entity là hoàn toàn hợp lý. Một đơn đặt hàng (purchase order) được gán một hạn mức tổng tiền tối đa cho phép, và tổng giá trị của tất cả các dòng sản phẩm (line item) không được vượt quá hạn mức đó. Quy tắc này trở nên rất phức tạp để thực thi khi nhiều người dùng cùng thêm các line item vào đồng thời. Một lượt thêm đơn lẻ có thể không vượt quá giới hạn, nhưng các thao tác thêm diễn ra đồng thời bởi nhiều người dùng khi gộp lại có thể cùng nhau vượt quá hạn mức. Tôi sẽ không lặp lại giải pháp ở đây, nhưng tôi muốn nhấn mạnh rằng trong phần lớn thời gian, các invariant của mô hình nghiệp vụ thường đơn giản hơn nhiều để quản lý so với ví dụ đó. Việc nhận thức được điều này giúp chúng ta mô hình hóa các Aggregate với càng ít thuộc tính càng tốt.

Các Aggregate nhỏ hơn không chỉ có hiệu năng và khả năng mở rộng tốt hơn, mà chúng còn có xu hướng thiên về thành công giao dịch (transactional success), nghĩa là các xung đột ngăn cản thao tác commit xảy ra rất hiếm khi. Điều này làm cho hệ thống trở nên dễ dùng hơn rất nhiều. Miền nghiệp vụ của bạn thường sẽ không có các ràng buộc bất biến thực sự đến mức ép bạn phải rơi vào tình huống thiết kế những cấu thành khổng lồ. Do đó, việc chủ động giới hạn kích thước Aggregate là một quyết định hết sức sáng suốt. Khi thỉnh thoảng bạn gặp phải một quy tắc nhất quán thực sự, hãy bổ sung thêm một vài Entity, hoặc có thể là một collection khi cần thiết, nhưng hãy luôn tự thúc đẩy bản thân giữ cho kích thước tổng thể càng nhỏ càng tốt.

## Đừng tin tưởng tuyệt đối vào mọi Use Case

Các chuyên viên phân tích nghiệp vụ (Business Analyst - BA) đóng vai trò quan trọng trong việc cung cấp các đặc tả use case (trường hợp sử dụng). Rất nhiều công sức được đổ vào một bản đặc tả lớn và chi tiết, và nó sẽ ảnh hưởng đến nhiều quyết định thiết kế của chúng ta. Dẫu vậy, chúng ta không được quên rằng các use case được tạo ra theo cách này thường không mang góc nhìn sâu sắc của các domain expert và lập trình viên trong đội ngũ mô hình hóa gắn kết của chúng ta. Chúng ta vẫn phải đối chiếu từng use case với mô hình và thiết kế hiện tại, bao gồm cả những quyết định về Aggregate. Một vấn đề thường nảy sinh là có một use case cụ thể nào đó yêu cầu phải sửa đổi nhiều instance của Aggregate. Trong trường hợp như vậy, chúng ta phải xác định xem liệu mục tiêu lớn đó của người dùng được phân bổ trên nhiều giao dịch lưu trữ, hay nó diễn ra chỉ trong đúng một giao dịch. Nếu rơi vào trường hợp thứ hai, chúng ta hoàn toàn có lý do để hoài nghi. Dù được viết tốt đến đâu, một use case như vậy có thể không phản ánh chính xác các Aggregate thực sự trong mô hình của chúng ta.

Giả định rằng các ranh giới Aggregate của bạn đã khớp với các ràng buộc nghiệp vụ thực tế, việc các chuyên viên phân tích nghiệp vụ đặc tả như những gì bạn thấy trong Hình 10.4 chắc chắn sẽ gây ra sự cố. Khi suy tính qua các hoán vị thứ tự commit khác nhau, bạn sẽ thấy có những trường hợp mà hai trong số ba yêu cầu sẽ thất bại. 5 Việc cố gắng thực hiện điều này cho thấy điều gì về thiết kế của bạn? Câu trả lời cho câu hỏi đó có thể mở đường cho sự hiểu biết sâu sắc hơn về miền nghiệp vụ. Việc cố gắng giữ cho nhiều instance của Aggregate nhất quán với nhau có thể đang ngầm báo hiệu rằng đội ngũ của bạn đã bỏ sót một invariant. Rất có thể cuối cùng bạn sẽ gộp nhiều Aggregate lại thành một khái niệm hoàn toàn mới với một tên gọi mới nhằm giải quyết quy tắc nghiệp vụ vừa được nhận diện. (Và tất nhiên, có thể chỉ một số phần của các Aggregate cũ được gộp vào Aggregate mới.)

5. Điều này không đề cập đến thực tế là một số use case mô tả việc sửa đổi nhiều Aggregate trải dài qua nhiều giao dịch khác nhau — điều đó hoàn toàn ổn. Một mục tiêu của người dùng (user goal) không nên bị đánh đồng là một giao dịch duy nhất. Chúng ta chỉ quan tâm đến những use case thực sự yêu cầu sửa đổi nhiều instance của Aggregate trong phạm vi một giao dịch duy nhất.

Hình 10.4 Hiện tượng tranh chấp đồng thời xảy ra giữa ba người dùng cùng cố gắng truy cập vào hai instance của Aggregate giống nhau, dẫn đến số lượng lớn các lỗi thất bại giao dịch.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000392_a178e10579c9b58c1f21851ddacb4b107ecb09872b8b36d538170ac86e7c8bdd.png)

Như vậy, một use case mới có thể đem lại những hiểu biết sâu sắc thôi thúc chúng ta tái mô hình hóa Aggregate, nhưng ở đây cũng cần phải giữ thái độ hoài nghi. Việc gom nhiều Aggregate thành một có thể làm lộ ra một khái niệm hoàn toàn mới với tên gọi mới, tuy nhiên nếu việc mô hình hóa khái niệm mới này lại dẫn dắt bạn tới việc thiết kế một Aggregate dạng cụm lớn, thì cuối cùng nó vẫn sẽ vướng phải tất cả các vấn đề cố hữu của hướng tiếp cận đó. Vậy có hướng tiếp cận nào khác có thể giúp ích?

Chỉ vì bạn được giao một use case đòi hỏi phải duy trì tính nhất quán trong một giao dịch duy nhất không có nghĩa là bạn bắt buộc phải làm như vậy. Thường thì trong những trường hợp như thế này, mục tiêu nghiệp vụ hoàn toàn có thể đạt được thông qua tính nhất quán sau cùng (eventual consistency) giữa các Aggregate. Đội ngũ phát triển cần phải xem xét các use case một cách có tư duy phản biện và chất vấn lại các giả định ban đầu, đặc biệt là khi việc làm theo đúng nguyên văn bản đặc tả sẽ dẫn tới những thiết kế cồng kềnh, khó quản lý. Đội ngũ có thể phải viết lại use case (hoặc ít nhất là hình dung lại nó nếu gặp phải một chuyên viên phân tích nghiệp vụ bất hợp tác). Use case mới sẽ đặc tả rõ tính nhất quán sau cùng cùng với độ trễ cập nhật được chấp nhận (acceptable update delay). Đây là một trong những vấn đề sẽ được đề cập sâu hơn ở phần sau của chương này.

## Quy tắc: Tham chiếu các Aggregate khác thông qua danh tính

Khi thiết kế Aggregate, chúng ta có thể mong muốn một cấu trúc cấu thành cho phép duyệt qua các đồ thị đối tượng có độ sâu lớn, nhưng đó hoàn toàn không phải là mục đích của pattern (mẫu hình thiết kế) này. [Evans] đã chỉ ra rằng một Aggregate có thể giữ các tham chiếu đến Root của các Aggregate khác. Tuy nhiên, chúng ta phải luôn ghi nhớ rằng điều này không hề đặt Aggregate được tham chiếu vào bên trong ranh giới nhất quán của Aggregate đang tham chiếu tới nó. Tham chiếu đó không tạo ra một Aggregate tổng thể duy nhất. Chúng vẫn là hai (hoặc nhiều hơn) Aggregate độc lập, như minh họa trong Hình 10.5.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000393_4b367da0877fe6e84bad43f90c41a3586daf9c3d5dd09b6281f6f242d3393b7b.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000394_054f0c4f2ebbb748f5b2cae947ff63d0d5c62d53f304e5854295967f745fb1de.png)

Trong Java, liên kết này sẽ được mô hình hóa như sau:

```java
public class BacklogItem extends ConcurrencySafeEntity {
    ...
    private Product product;
    ...
}

```

Nghĩa là, `BacklogItem` nắm giữ một liên kết đối tượng trực tiếp tới `Product`.

Kết hợp với những gì đã thảo luận và những nội dung tiếp theo, điều này mang lại một vài hệ quả:

1. Cả Aggregate đang tham chiếu (`BacklogItem`) và Aggregate được tham chiếu (`Product`) đều tuyệt đối không được phép bị sửa đổi trong cùng một giao dịch. Chỉ một trong hai đối tượng được phép sửa đổi trong phạm vi một giao dịch đơn lẻ.
2. Nếu bạn đang sửa đổi nhiều instance trong một giao dịch duy nhất, đó có thể là một dấu hiệu rõ ràng cho thấy các ranh giới nhất quán của bạn đã bị đặt sai. Nếu đúng như vậy, rất có thể bạn đã bỏ lỡ một cơ hội mô hình hóa quý giá; một khái niệm trong Ubiquitous Language (ngôn ngữ chung / ngôn ngữ toàn hiện giữa nghiệp vụ và kỹ thuật) vẫn chưa được khai phá dù nó đang "vẫy tay và gào thét" ngay trước mặt bạn (xem phần trước của chương này).

Hình 10.5 Có hai Aggregate riêng biệt, chứ không phải một.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000395_2181c1030d9fd31109c59a9c05d53556f70515e4a70c9fc9b1871e7379db3056.png)

3. Nếu bạn cố gắng áp dụng điểm 2 và việc đó lại dẫn tới một Aggregate dạng cụm lớn với toàn bộ những cảnh báo đã nêu trước đây, thì đó có thể là dấu hiệu cho thấy bạn cần sử dụng tính nhất quán sau cùng (xem phần sau của chương này) thay vì tính nhất quán nguyên tử (atomic consistency).

Nếu bạn không giữ bất kỳ tham chiếu nào, bạn không thể sửa đổi một Aggregate khác. Vì vậy, sự cám dỗ muốn sửa đổi nhiều Aggregate trong cùng một giao dịch có thể bị dập tắt ngay từ đầu bằng cách tránh tạo ra tình huống này. Tuy nhiên, điều đó lại quá hạn chế vì các mô hình miền luôn đòi hỏi một số mối liên kết nhất định. Vậy chúng ta có thể làm gì để vừa tạo thuận lợi cho các liên kết cần thiết, vừa phòng ngừa việc lạm dụng giao dịch hay các lỗi thất bại quá mức, đồng thời cho phép mô hình đạt hiệu năng cao và mở rộng tốt?

## Giúp các Aggregate phối hợp hoạt động thông qua tham chiếu danh tính

Hãy ưu tiên việc chỉ tham chiếu tới các Aggregate bên ngoài thông qua định danh duy nhất toàn cục (globally unique identity) của chúng, thay vì nắm giữ một tham chiếu đối tượng trực tiếp (hoặc "con trỏ"). Điều này được minh họa trong Hình 10.6.

Hình 10.6 Aggregate BacklogItem suy luận các liên kết ngoài ranh giới của nó thông qua danh tính

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000396_4deed4044cec30ece3d7e13534c8014aea279f6eb93db7a1aabea1b3bcc6bf01.png)

361

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000397_73d69aece5001aef089b96bad8acbd7c321df5c694b4a2428c97414f5aab6492.png)

Chúng ta sẽ tái cấu trúc mã nguồn thành:

```java
public class BacklogItem extends ConcurrencySafeEntity {

```

```java
    ...
    private ProductId productId;
    ...
}

```

Các Aggregate sử dụng tham chiếu đối tượng suy luận (inferred object reference) theo cách này sẽ tự động có kích thước nhỏ hơn vì các tham chiếu không bao giờ bị nạp tức thời (eagerly loaded). Mô hình có thể đạt hiệu năng tốt hơn vì các instance tốn ít thời gian nạp hơn và chiếm ít bộ nhớ hơn. Việc sử dụng ít bộ nhớ mang lại những tác động tích cực đối với cả chi phí cấp phát bộ nhớ (allocation overhead) lẫn hoạt động thu gom rác (garbage collection).

## Điều hướng mô hình

Việc tham chiếu theo định danh không hoàn toàn ngăn cản khả năng điều hướng xuyên suốt mô hình. Một số người sẽ sử dụng một Repository (12) (kho lưu trữ đối tượng miền) từ ngay bên trong một Aggregate để tra cứu dữ liệu. Kỹ thuật này được gọi là Disconnected Domain Model (mô hình miền ngắt kết nối), và thực chất nó là một dạng nạp lười (lazy loading). Tuy nhiên, có một cách tiếp cận khác được khuyến nghị hơn: Hãy sử dụng một Repository hoặc Domain Service (7) (dịch vụ miền) để tra cứu các đối tượng phụ thuộc trước khi gọi hành vi của Aggregate. Một Application Service phía client có thể kiểm soát quá trình này, sau đó ủy thác (dispatch) tới Aggregate:

```java
public class ProductBacklogItemService ... {
    ...
    @Transactional
    public void assignTeamMemberToTask(
        String aTenantId,
        String aBacklogItemId,
        String aTaskId,
        String aTeamMemberId) {

    BacklogItem backlogItem =
        backlogItemRepository.backlogItemOfId(
            new TenantId(aTenantId),
            new BacklogItemId(aBacklogItemId));

    Team ofTeam =
        teamRepository.teamOfId(
            backlogItem.tenantId(),
            backlogItem.teamId());

    backlogItem.assignTeamMemberToTask(
        new TeamMemberId(aTeamMemberId),

```

ofTeam, new TaskId(aTaskId));

}

...

}

Việc để một Application Service giải quyết các quan hệ phụ thuộc giúp giải phóng Aggregate khỏi việc phải phụ thuộc vào Repository hay Domain Service. Tuy nhiên, đối với các trường hợp giải quyết phụ thuộc rất phức tạp và đặc thù cho miền nghiệp vụ, việc truyền một Domain Service vào một phương thức command của Aggregate có thể là giải pháp tối ưu nhất. Khi đó, Aggregate có thể thực hiện double-dispatch (cơ chế ủy thác hai lần) tới Domain Service để phân giải các tham chiếu. Xin nhắc lại, bất kể Aggregate này truy cập vào các Aggregate khác theo cách nào đi nữa, việc tham chiếu đến nhiều Aggregate trong một yêu cầu duy nhất không đồng nghĩa với việc bạn có quyền gây ra sửa đổi trên từ hai Aggregate trở lên.

## Tư duy cao bồi

* LB: "Tôi có hai điểm tham chiếu khi định hướng đường đi vào ban đêm. Nếu ngửi thấy mùi thịt bò còn sống trên móng guốc, tôi biết mình đang đi về phía đàn bò. Còn nếu ngửi thấy mùi thịt bò đang nướng trên vỉ than, tôi biết mình đang đi về nhà."

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000398_f0602e08044d8dc749009cb98266b0e6849ae5c454a984ad7c9bcb637e2f9b81.png)

> 💡 **Giải thích thêm:** "Beef on the hoof" (thịt bò còn trên móng guốc) là thành ngữ chỉ đàn bò sống đang đi lại ngoài đồng cỏ; còn "beef on the grill" (thịt bò trên vỉ nướng) chỉ món ăn đã sẵn sàng trên bàn ăn gia đình. Câu nói hóm hỉnh này ẩn dụ về **Model Navigation** và điểm tham chiếu trong kiến trúc phần mềm: bạn chỉ cần các điểm mốc tham chiếu rõ ràng, tối giản (ở đây là ID của Aggregate) để định hướng và biết chính xác mình đang thao tác với cái gì, thay vì phải tải và ôm đồm toàn bộ cả đàn bò (cả đồ thị đối tượng phức tạp).
> (Không có nguồn trích dẫn xác thực — cần tự kiểm chứng thêm)

Việc giới hạn mô hình chỉ sử dụng tham chiếu theo định danh có thể khiến việc phục vụ các client chuyên tổng hợp và hiển thị giao diện người dùng (User Interface - UI (14)) trở nên khó khăn hơn. Bạn có thể phải sử dụng nhiều Repository trong một use case duy nhất chỉ để đổ dữ liệu vào view. Nếu chi phí truy vấn gây ra các vấn đề về hiệu năng, bạn nên cân nhắc sử dụng theta join hoặc CQRS (Command Query Responsibility Segregation - phân tách trách nhiệm giữa đọc và ghi). Ví dụ, Hibernate hỗ trợ theta join như một phương tiện để tổng hợp dữ liệu từ một số instance của Aggregate được liên kết theo tham chiếu chỉ trong một câu truy vấn join duy nhất, giúp cung cấp đủ các thành phần cần thiết để hiển thị. Nếu cả CQRS và theta join đều không khả thi, bạn có thể cần phải tìm kiếm sự cân bằng giữa tham chiếu đối tượng suy luận (qua ID) và tham chiếu đối tượng trực tiếp.

Nếu tất cả những lời khuyên này dường như dẫn tới một mô hình kém tiện lợi hơn, hãy xem xét các lợi ích bổ sung mà nó đem lại. Việc làm cho các Aggregate nhỏ hơn không chỉ giúp mô hình đạt hiệu năng cao hơn, mà chúng ta còn có thể dễ dàng bổ sung khả năng mở rộng (scalability) và xử lý phân tán (distribution).

## Khả năng mở rộng và Kiến trúc phân tán

Vì các Aggregate không sử dụng tham chiếu trực tiếp đến các Aggregate khác mà tham chiếu qua danh tính, trạng thái lưu trữ của chúng có thể được dịch chuyển linh hoạt giữa các phân vùng lưu trữ để đạt tới quy mô rất lớn. Khả năng mở rộng gần như vô hạn có thể đạt được bằng cách cho phép liên tục tái phân vùng (repartitioning) kho lưu trữ dữ liệu của Aggregate, như đã được Pat Helland (thuộc Amazon.com) giải thích trong bài tham luận "Life beyond Distributed Transactions: An Apostate's Opinion" [Helland]. Khái niệm mà chúng ta gọi là Aggregate thì ông gọi là entity. Nhưng dù gọi dưới cái tên nào, điều ông mô tả thực chất vẫn là một Aggregate: một đơn vị cấu thành sở hữu tính nhất quán cấp giao dịch. Một số cơ chế lưu trữ NoSQL hỗ trợ dạng lưu trữ phân tán lấy cảm hứng từ Amazon này. Chúng cung cấp phần lớn những gì mà [Helland] gọi là tầng dưới có nhận thức về khả năng mở rộng (scale-aware layer). Khi triển khai một kho lưu trữ phân tán, hoặc ngay cả khi sử dụng một cơ sở dữ liệu SQL với mục đích tương tự, việc tham chiếu qua danh tính đóng vai trò vô cùng trọng yếu.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000399_ac307a3e5d561f0fa425106d2888d177dfd28a8c468a66dc4f5f7ea4f1513690.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000400_7bb3f2f682405dfc06931273c7f4b6e50edb1b5e7432823cb993e3e6bce09f17.png)

Tính phân tán không chỉ dừng lại ở phạm vi lưu trữ. Do luôn có nhiều Bounded Context cùng tham gia vận hành trong một sáng kiến Core Domain (miền cốt lõi), việc tham chiếu theo danh tính cho phép các mô hình miền phân tán duy trì các liên kết từ xa. Khi áp dụng phương pháp tiếp cận hướng sự kiện (Event-Driven), các Domain Event (8) (sự kiện miền) dựa trên tin nhắn có chứa định danh của Aggregate sẽ được phát đi khắp hệ thống doanh nghiệp. Các bên đăng ký nhận tin (message subscriber) trong các Bounded Context bên ngoài sẽ sử dụng các định danh này để thực thi các nghiệp vụ trong mô hình miền của riêng họ. Tham chiếu theo danh tính thiết lập nên các liên kết từ xa hay các đối tác cộng tác (partners). Các thao tác phân tán được quản lý thông qua những gì mà [Helland] gọi là "hoạt động hai bên" (two-party activities), nhưng theo thuật ngữ của mẫu hình Publish-Subscribe [Buschmann et al.] hoặc Observer [Gamma et al.], đó là hoạt động đa bên (từ hai bên trở lên). Các giao dịch trải rộng trên các hệ thống phân tán không mang tính nguyên tử (non-atomic). Các hệ thống khác nhau sẽ dần dần đưa nhiều Aggregate về trạng thái nhất quán sau cùng.

## Quy tắc: Sử dụng tính nhất quán sau cùng bên ngoài ranh giới

Có một nhận định thường bị bỏ qua trong định nghĩa về pattern Aggregate của [Evans]. Nó ảnh hưởng rất lớn đến những gì chúng ta phải làm để đạt được tính nhất quán cho mô hình khi nhiều Aggregate buộc phải bị tác động bởi một yêu cầu duy nhất từ client:

> Bất kỳ quy tắc nào trải rộng qua nhiều AGGREGATE đều sẽ không được kỳ vọng là phải cập nhật mới nhất tại mọi thời điểm. Thông qua việc xử lý sự kiện, xử lý theo lô (batch processing), hoặc các cơ chế cập nhật khác, các phụ thuộc khác có thể được giải quyết trong một khoảng thời gian nhất định nào đó. [Evans, tr. 128]

Vì vậy, nếu việc thực thi một command trên một instance của Aggregate đòi hỏi các quy tắc nghiệp vụ bổ sung phải được thực thi trên một hoặc nhiều Aggregate khác, hãy sử dụng eventual consistency. Việc chấp nhận thực tế rằng tất cả các instance của Aggregate trong một doanh nghiệp quy mô lớn, lưu lượng truy cập cao không bao giờ hoàn toàn nhất quán tại cùng một thời điểm sẽ giúp chúng ta dễ dàng chấp nhận rằng tính nhất quán sau cùng cũng hoàn toàn hợp lý ở quy mô nhỏ hơn, nơi chỉ có một vài instance tham gia.

Hãy hỏi các domain expert xem liệu họ có thể chấp nhận một khoảng thời gian trễ nhất định giữa việc sửa đổi một instance này và các instance liên quan khác hay không. Các chuyên gia nghiệp vụ đôi khi cảm thấy thoải mái hơn nhiều với ý tưởng về tính nhất quán có độ trễ so với các lập trình viên. Họ nhận thức rõ những độ trễ thực tế luôn diễn ra hàng ngày trong hoạt động kinh doanh của mình, trong khi các lập trình viên thường bị "ăn sâu vào tiềm thức" tư duy thay đổi nguyên tử tức thời. Các chuyên gia nghiệp vụ thường nhớ về thời kỳ trước khi các hoạt động kinh doanh được tự động hóa bằng máy tính, khi mà đủ loại độ trễ diễn ra liên miên và tính nhất quán không bao giờ đến ngay tức thì. Do đó, các chuyên gia nghiệp vụ thường rất sẵn lòng cho phép các độ trễ hợp lý — một khoảng thời gian hào phóng tính bằng giây, phút, giờ, hoặc thậm chí là nhiều ngày — trước khi dữ liệu đạt trạng thái nhất quán.

Có một cách rất thực tế để hỗ trợ tính nhất quán sau cùng trong một mô hình DDD. Một phương thức command của Aggregate sẽ phát hành (publish) một Domain Event, sự kiện này sau đó sẽ được chuyển phát kịp thời đến một hoặc nhiều bên đăng ký bất đồng bộ (asynchronous subscriber):

```java
public class BacklogItem extends ConcurrencySafeEntity {

```

```java
    ...
    public void commitTo(Sprint aSprint) {
        ...
        DomainEventPublisher
            .instance()
            .publish(new BacklogItemCommitted(
                this.tenantId(),
                this.backlogItemId(),
                this.sprintId()));
    }
    ...
}

```

Mỗi subscriber này sau đó sẽ truy xuất một instance Aggregate khác nhưng tương ứng và thực thi hành vi dựa trên nó. Mỗi subscriber chạy trong một giao dịch độc lập, tuân thủ nghiêm ngặt quy tắc của Aggregate là chỉ sửa đổi đúng một instance trên mỗi giao dịch.

Điều gì sẽ xảy ra nếu subscriber gặp phải tình trạng tranh chấp đồng thời với một client khác, khiến cho thao tác sửa đổi của nó bị thất bại? Thao tác sửa đổi hoàn toàn có thể được thử lại (retry) nếu subscriber không gửi phản hồi xác nhận thành công (acknowledgement) về cơ chế truyền thông điệp. Thông điệp sẽ được gửi lại, một giao dịch mới được khởi tạo, một nỗ lực mới được thực hiện để thực thi command cần thiết, và một lượt commit tương ứng được tiến hành. Quy trình thử lại này có thể tiếp diễn cho đến khi đạt được tính nhất quán, hoặc cho đến khi chạm mức giới hạn thử lại. 6 Nếu thất bại hoàn toàn, hệ thống có thể cần thực hiện giao dịch bù trừ (compensating transaction), hoặc tối thiểu là phải báo cáo lỗi để chờ can thiệp xử lý.

Việc phát hành Domain Event `BacklogItemCommitted` trong ví dụ cụ thể này mang lại kết quả gì? Cần nhớ lại rằng `BacklogItem` đã nắm giữ định danh của `Sprint` mà nó được cam kết thực hiện, chúng ta hoàn toàn không muốn duy trì một mối liên kết hai chiều vô nghĩa. Thay vào đó, sự kiện này cho phép tạo ra một `CommittedBacklogItem` theo cơ chế nhất quán sau cùng để `Sprint` có thể ghi nhận lại cam kết công việc. Vì mỗi `CommittedBacklogItem` đều có một thuộc tính biểu thị thứ tự (ordering), nó cho phép `Sprint` gán cho mỗi `BacklogItem` một thứ tự khác biệt so với thứ tự trong `Product` và `Release`, đồng thời không bị ràng buộc vào ước lượng về `BusinessPriority` (độ ưu tiên nghiệp vụ) được ghi nhận trên chính instance của `BacklogItem`. Tương tự, `Product` và `Release` cũng nắm giữ các liên kết tương tự, lần lượt là `ProductBacklogItem` và `ScheduledBacklogItem`.

6. Hãy cân nhắc thực hiện thử lại bằng thuật toán Capped Exponential Back-off (thử lại lùi số mũ có giới hạn trần). Thay vì mặc định thử lại sau mỗi N giây cố định, hãy tăng thời gian chờ thử lại theo cấp số nhân kết hợp đặt một mức trần giới hạn trên cho thời gian chờ. Ví dụ: bắt đầu ở mức 1 giây và lùi dần theo cấp số nhân, nhân đôi thời gian chờ cho đến khi thành công hoặc chạm mức trần 32 giây chờ và thử lại.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000401_f147817898df881e02a25877c18653575ece843a08f44490f6252d0f73bba3ca.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000402_349cee9cc8a01558ac6eb1c2f28b4c3055bfa0561eba5de24549e7d5a0f4d047.png)

## Giờ thực hành trên bảng trắng

* Hãy quay trở lại danh sách các Aggregate dạng cụm lớn và những trường hợp từ hai Aggregate trở lên bị sửa đổi trong một giao dịch đơn lẻ.
* Mô tả và vẽ sơ đồ cách bạn sẽ chia nhỏ các cụm lớn đó. Khoanh tròn và ghi chú từng bất biến thực sự bên trong mỗi Aggregate nhỏ mới.
* Mô tả và vẽ sơ đồ cách bạn sẽ duy trì tính nhất quán sau cùng giữa các Aggregate riêng biệt.

Ví dụ này minh họa cách sử dụng tính nhất quán sau cùng trong một Bounded Context đơn lẻ, nhưng kỹ thuật tương tự cũng có thể được áp dụng theo phương thức phân tán như đã mô tả trước đó.

## Hãy tự hỏi: Đó là nhiệm vụ của ai?

Một số kịch bản nghiệp vụ có thể khiến việc xác định nên sử dụng tính nhất quán giao dịch hay tính nhất quán sau cùng trở nên vô cùng khó khăn. Những người áp dụng DDD theo cách cổ điển/truyền thống thường có xu hướng nghiêng về tính nhất quán giao dịch. Những người theo trường phái CQRS lại có xu hướng nghiêng về tính nhất quán sau cùng. Nhưng hướng nào mới là đúng? Thành thực mà nói, không có xu hướng nào trong số đó đưa ra được câu trả lời bắt nguồn từ chính miền nghiệp vụ, mà đó chỉ là sở thích kỹ thuật thuần túy. Liệu có cách nào tốt hơn để phân xử trường hợp này?

## Tư duy cao bồi

* LB: "Con trai tôi bảo nó vừa tìm thấy trên mạng Internet cách làm cho đàn bò cái nhà tôi mắn đẻ hơn. Tôi bảo nó: 'Đấy là việc của con bò đực'."

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000403_53775a4132130e38981219bf60d616e22de192813703273f3d39a98350874ad8.png)

> 💡 **Giải thích thêm:** Câu chuyện ngụ ngôn hóm hỉnh nhấn mạnh nguyên lý **Separation of Concerns (phân tách trách nhiệm)** và **Role Responsibility**: trong thiết kế phần mềm, đừng để một thành phần cố làm thay công việc vốn thuộc về bản chất của đối tượng hoặc hệ thống khác. Khi phân vân giữa Transactional Consistency và Eventual Consistency, hãy tự hỏi: "Đó là nhiệm vụ của ai?" — nếu đó là nhiệm vụ trực tiếp của người dùng đang thao tác, hãy đảm bảo bằng giao dịch; còn nếu là nhiệm vụ của người khác hoặc của hệ thống xử lý ngầm, hãy để dữ liệu đạt trạng thái nhất quán sau cùng (eventual consistency).
> (Không có nguồn trích dẫn xác thực — cần tự kiểm chứng thêm)

Khi thảo luận điều này với Eric Evans, một chỉ dẫn vô cùng đơn giản nhưng rất xác đáng đã được hé lộ. Khi xem xét use case (hoặc user story), hãy tự hỏi xem: Liệu việc làm cho dữ liệu trở nên nhất quán có phải là nhiệm vụ của người dùng đang thực thi use case đó hay không? Nếu đúng, hãy cố gắng đảm bảo tính nhất quán cấp giao dịch, nhưng chỉ thực hiện bằng cách tuân thủ nghiêm ngặt các quy tắc khác của Aggregate. Nếu đó là nhiệm vụ của một người dùng khác, hoặc là trách nhiệm của hệ thống, hãy để cho dữ liệu đạt tính nhất quán sau cùng. Chút kinh nghiệm quý báu đó không chỉ đóng vai trò là một yếu tố phân xử thuận tiện, mà nó còn giúp chúng ta thấu hiểu miền nghiệp vụ sâu sắc hơn rất nhiều. Nó vạch trần các bất biến thực sự của hệ thống: những quy tắc bắt buộc phải được duy trì nhất quán ở cấp độ giao dịch. Sự hiểu biết đó có giá trị hơn nhiều so với việc chỉ mặc định chọn theo một thiên kiến kỹ thuật.

Đây là một mẹo tuyệt vời để bổ sung vào bộ "Nguyên tắc kinh nghiệm cho Aggregate". Do còn có những yếu tố tác động khác cần xem xét, chỉ dẫn này có thể không phải lúc nào cũng đưa ra lựa chọn cuối cùng giữa tính nhất quán giao dịch và nhất quán sau cùng, nhưng nó thường cung cấp cái nhìn sâu sắc hơn về mô hình. Chỉ dẫn này sẽ được áp dụng ở phần sau của chương khi đội ngũ phát triển xem xét lại các ranh giới Aggregate của họ.

## Những lý do để phá vỡ quy tắc

Một người thực hành DDD dày dạn kinh nghiệm đôi khi có thể quyết định lưu lại các thay đổi trên nhiều instance của Aggregate trong một giao dịch duy nhất, nhưng điều đó chỉ diễn ra khi có lý do thực sự chính đáng. Vậy những lý do đó có thể là gì? Tôi sẽ thảo luận về bốn lý do ở đây. Bạn có thể gặp phải những lý do này hoặc những trường hợp khác.

## Lý do thứ nhất: Sự thuận tiện của giao diện người dùng

Đôi khi giao diện người dùng, vì lý do thuận tiện, cho phép người dùng định nghĩa các đặc tính chung của nhiều đối tượng cùng một lúc nhằm tạo chúng theo lô (batch). Có thể tình huống các thành viên trong đội ngũ muốn tạo hàng loạt backlog item theo lô diễn ra rất thường xuyên. Giao diện người dùng cho phép họ điền tất cả các thuộc tính chung vào một phần, và sau đó lần lượt nhập một vài thuộc tính riêng biệt của từng mục, giúp loại bỏ các thao tác lặp đi lặp lại. Toàn bộ các backlog item mới sau đó sẽ được lên kế hoạch (tạo mới) cùng một lúc:

```java
public class ProductBacklogItemService ... {
    ...
    @Transactional
    public void planBatchOfProductBacklogItems(
        String aTenantId,
        String productId,
        BacklogItemDescription[] aDescriptions) {

    Product product =
        productRepository.productOfId(
            new TenantId(aTenantId),
            new ProductId(productId));

```

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000404_ca8aeae62a54b0a28852e04b84f6a54835fb86e2e7e142b3f86d4997335fee47.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000405_8633574c7adeb3292757973ddafd395145f53f1863e502bd2bddb828bbb9a4f1.png)

```java
    for (BacklogItemDescription desc : aDescriptions) {
        BacklogItem plannedBacklogItem =
            product.planBacklogItem(
                desc.summary(),
                desc.category(),
                BacklogItemType.valueOf(
                    desc.backlogItemType()),
                StoryPoints.valueOf(
                    desc.storyPoints()));

        backlogItemRepository.add(plannedBacklogItem);
    }
}
...
}

```

Điều này có gây ra vấn đề gì đối với việc quản lý các invariant hay không? Trong trường hợp này là không, vì việc chúng được tạo từng cái một hay tạo theo lô đều không tạo ra sự khác biệt. Các đối tượng đang được khởi tạo là các Aggregate hoàn chỉnh, và bản thân chúng tự duy trì các invariant của riêng mình. Do đó, nếu việc tạo hàng loạt các instance của Aggregate cùng một lúc về mặt ngữ nghĩa không hề khác biệt so với việc tạo từng đối tượng một cách lặp đi lặp lại, thì đây là một lý do cho phép bạn phá vỡ quy tắc kinh nghiệm mà không phải chịu bất kỳ hậu quả tiêu cực nào.

## Lý do thứ hai: Thiếu thốn các cơ chế kỹ thuật hỗ trợ

Tính nhất quán sau cùng đòi hỏi phải sử dụng một dạng năng lực xử lý ngoài luồng (out-of-band processing), chẳng hạn như hệ thống truyền thông điệp (messaging), bộ định thời (timer), hoặc các tiến trình nền (background thread). Điều gì sẽ xảy ra nếu dự án bạn đang làm việc hoàn toàn không có sự chuẩn bị hay hỗ trợ cho bất kỳ cơ chế nào như vậy? Mặc dù hầu hết chúng ta sẽ thấy điều đó thật kỳ lạ, nhưng bản thân tôi đã từng đối mặt với đúng sự hạn chế này. Khi không có cơ chế truyền thông điệp, không có timer chạy ngầm và cũng không có bất kỳ năng lực xử lý đa luồng tự xây dựng nào, chúng ta có thể làm gì?

Nếu không cẩn thận, tình huống này có thể kéo chúng ta quay trở lại việc thiết kế các Aggregate dạng cụm lớn. Mặc dù điều đó có thể mang lại cho chúng ta cảm giác như mình đang tuân thủ quy tắc một giao dịch duy nhất, nhưng như đã thảo luận trước đó, nó cũng sẽ làm suy giảm hiệu năng và hạn chế khả năng mở rộng. Để tránh điều đó, có lẽ chúng ta có thể thay đổi hoàn toàn các Aggregate của hệ thống, buộc mô hình phải tự giải quyết các thách thức kỹ thuật của chúng ta. Chúng ta cũng đã xem xét khả năng các bản đặc tả của dự án có thể bị bảo vệ một cách cứng nhắc, khiến chúng ta có rất ít không gian để thương lượng về những khái niệm miền nghiệp vụ chưa từng được hình dung trước đó. Đó thực sự không phải là cách làm chuẩn của DDD, nhưng đôi khi điều đó vẫn xảy ra trong thực tế. Các điều kiện khách quan có thể không cho phép có bất kỳ giải pháp hợp lý nào để xoay chuyển hoàn cảnh mô hình hóa theo hướng có lợi cho chúng ta. Trong những trường hợp như vậy, thực tế vận hành dự án có thể buộc chúng ta phải sửa đổi từ hai instance của Aggregate trở lên trong một giao dịch. Dù quyết định này có vẻ hiển nhiên đến đâu, bạn cũng không nên đưa ra một cách quá vội vàng.

## Tư duy cao bồi

AJ: "Nếu bạn nghĩ rằng luật lệ sinh ra là để bị phá vỡ, tốt hơn hết bạn nên quen biết một thợ sửa chữa lành nghề."

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000406_648960dd520450d39b3a1e289c5434b3819c6e9b8390c9ba972dc49abf89e8f8.png)

> 💡 **Giải thích thêm:** Câu nói này là lời cảnh tỉnh sắc sảo về việc thỏa hiệp kiến trúc: việc phá vỡ nguyên tắc thiết kế (như sửa đổi nhiều Aggregate trong cùng một transaction) luôn để lại những khoản nợ kỹ thuật (technical debt) và rủi ro tranh chấp tài nguyên nghiêm trọng. Nếu quyết định phá lệ, bạn bắt buộc phải có kiến thức chuyên sâu và phương án phòng ngừa sự cố vững chắc ("thợ sửa chữa giỏi") để khắc phục hậu quả.
> (Không có nguồn trích dẫn xác thực — cần tự kiểm chứng thêm)

Hãy cân nhắc thêm một yếu tố bổ sung có thể củng cố thêm cho việc phá lệ: user-aggregate affinity (mức độ gắn kết giữa người dùng và Aggregate). Liệu các luồng công việc nghiệp vụ có đảm bảo rằng tại bất kỳ thời điểm nào cũng chỉ có duy nhất một người dùng tập trung thao tác trên một tập hợp các instance của Aggregate hay không? Việc đảm bảo tính gắn kết giữa người dùng và Aggregate làm cho quyết định thay đổi nhiều instance của Aggregate trong một giao dịch trở nên hợp lý hơn, vì nó có xu hướng ngăn ngừa sự vi phạm các invariant và hạn chế va chạm giao dịch. Ngay cả khi có sự gắn kết giữa người dùng và Aggregate, trong những tình huống hiếm hoi, người dùng vẫn có thể đối mặt với các xung đột đồng thời. Tuy nhiên, mỗi Aggregate vẫn sẽ được bảo vệ khỏi điều đó bằng cách sử dụng cơ chế optimistic concurrency. Dù sao đi nữa, xung đột đồng thời có thể xảy ra trong bất kỳ hệ thống nào, và thậm chí còn thường xuyên hơn khi sự gắn kết người dùng - Aggregate không đứng về phía chúng ta. Hơn nữa, việc phục hồi sau các xung đột đồng thời là tương đối đơn giản nếu chúng chỉ xảy ra với tần suất rất hiếm. Do đó, khi thiết kế rơi vào thế bắt buộc, đôi khi việc sửa đổi nhiều instance của Aggregate trong một giao dịch vẫn mang lại kết quả tốt.

## Lý do thứ ba: Giao dịch toàn cục

Một yếu tố ảnh hưởng khác cần được xem xét là tác động từ các công nghệ kế thừa (legacy technology) và các chính sách của doanh nghiệp. Một trong số đó có thể là yêu cầu bắt buộc phải tuân thủ nghiêm ngặt việc sử dụng các giao dịch toàn cục (global transaction) với cơ chế commit hai pha (two-phase commit). Đây là một trong những tình huống gần như không thể bác bỏ hay từ chối, ít nhất là trong ngắn hạn.

Ngay cả khi bắt buộc phải sử dụng một giao dịch toàn cục, bạn cũng không nhất thiết phải sửa đổi nhiều instance của Aggregate cùng lúc trong Bounded Context cục bộ của mình. Nếu bạn có thể tránh được điều đó, tối thiểu bạn vẫn ngăn ngừa được sự tranh chấp giao dịch trong Core Domain của mình và thực sự tuân thủ các quy tắc của Aggregate trong phạm vi tối đa có thể. Mặt trái của các giao dịch toàn cục là hệ thống của bạn nhiều khả năng sẽ không bao giờ có thể mở rộng được như kỳ vọng nếu bạn không thể loại bỏ cơ chế commit hai pha cùng tính nhất quán tức thời đi kèm với chúng.

## Lý do thứ tư: Hiệu năng truy vấn

Có những thời điểm mà việc nắm giữ các tham chiếu đối tượng trực tiếp tới các Aggregate khác lại là giải pháp tốt nhất. Điều này có thể được sử dụng để giảm thiểu các vấn đề về hiệu năng truy vấn của Repository. Những trường hợp này phải được cân nhắc hết sức cẩn trọng dưới lăng kính về kích thước tiềm ẩn và sự đánh đổi hiệu năng tổng thể. Một ví dụ về việc phá vỡ quy tắc tham chiếu theo định danh sẽ được trình bày ở phần sau của chương này.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000407_d9c3a51731145a3a507b4e290f01bf255e216fb4d14b8848982098c85d671351.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000408_7c8496648f52f347486b98a6b31d45febe1ed58acdc373585c0e134a4c125990.png)

## Tuân thủ các quy tắc

Bạn có thể gặp phải các quyết định thiết kế giao diện người dùng, các giới hạn kỹ thuật, các chính sách cứng nhắc, hoặc những yếu tố khác trong môi trường doanh nghiệp buộc bạn phải đưa ra một số thỏa hiệp. Chắc chắn chúng ta không chủ động đi tìm kiếm những cái cớ để phá vỡ bộ "Nguyên tắc kinh nghiệm cho Aggregate". Xét về lâu dài, việc tuân thủ các quy tắc sẽ mang lại lợi ích to lớn cho các dự án của chúng ta. Chúng ta sẽ có được tính nhất quán ở những nơi thực sự cần thiết, đồng thời nâng đỡ cho những hệ thống đạt hiệu năng tối ưu và khả năng mở rộng vượt trội.

## Thu nhận hiểu biết sâu sắc thông qua quá trình khám phá

Khi các quy tắc của Aggregate được đưa vào áp dụng, chúng ta sẽ thấy việc tuân thủ chúng tác động như thế nào đến thiết kế của mô hình SaaSOvation Scrum. Chúng a sẽ thấy đội ngũ dự án tư duy lại thiết kế của họ một lần nữa, áp dụng những kỹ thuật mới vừa được khám phá. Nỗ lực đó dẫn đến việc khám phá ra những góc nhìn sâu sắc mới về mô hình. Nhiều ý tưởng khác nhau của họ lần lượt được thử nghiệm và sau đó được thay thế bởi những giải pháp tối ưu hơn.

## Tái tư duy thiết kế, một lần nữa

Sau vòng lặp tái cấu trúc giúp chia nhỏ cụm lớn `Product`, giờ đây `BacklogItem` đứng độc lập như một Aggregate của riêng mình. Nó phản ánh mô hình được trình bày trong Hình 10.7. Đội ngũ đã gom một tập hợp các instance của `Task` vào bên trong Aggregate `BacklogItem`. Mỗi `BacklogItem` đều sở hữu một định danh duy nhất toàn cục: `BacklogItemId`. Mọi liên kết đến các Aggregate khác đều được suy luận thông qua định danh. Điều đó có nghĩa là `Product` cha của nó, `Release` mà nó được lên lịch, và `Sprint` mà nó được cam kết đều được tham chiếu qua các ID. Trông nó có vẻ khá nhỏ gọn.

Với việc đội ngũ hiện đang vô cùng hào hứng với việc thiết kế các Aggregate nhỏ, liệu họ có khả năng làm quá tay theo hướng đó hay không?

Bất chấp cảm giác tích cực có được từ vòng lặp trước đó, vẫn còn một số mối lo ngại tồn tại. Ví dụ, thuộc tính `story` cho phép chứa một lượng văn bản khá lớn. Các nhóm phát triển user story theo Agile sẽ không viết những đoạn văn dài dòng. Dẫu vậy, hệ thống lại có một thành phần soạn thảo tùy chọn hỗ trợ việc viết các định nghĩa use case phong phú. Những văn bản đó có thể lên tới nhiều nghìn byte. Đây là điều rất đáng để cân nhắc về chi phí phụ trội tiềm ẩn.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000409_6ae7c0d90c9240f5723997479803fe98dbdfef24bf0a807b2b1f0f0d8629541a.png)

Hình 10.7 Aggregate BacklogItem cấu thành hoàn chỉnh

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000410_f8ce209eeb7eab5440938b6b1c13f6e44f197567cebb886c3cf281ee921357e5.png)

Trước chi phí phụ trội tiềm tàng này cùng với những sai lầm đã gặp phải khi thiết kế cụm `Product` khổng lồ trong Hình 10.1 và Hình 10.3, đội ngũ dự án lúc này đặt ra sứ mệnh phải cắt giảm kích thước của mọi Aggregate trong Bounded Context. Những câu hỏi cốt tử bắt đầu xuất hiện. Liệu có tồn tại một invariant thực sự giữa `BacklogItem` và `Task` mà mối quan hệ này bắt buộc phải duy trì hay không? Hay đây lại là một trường hợp khác mà mối liên kết có thể tiếp tục được phân tách sâu hơn, để hình thành nên hai Aggregate riêng biệt một cách an toàn? Tổng cái giá phải trả nếu giữ nguyên thiết kế hiện tại sẽ là bao nhiêu?

Chìa khóa giúp họ đưa ra quyết định đúng đắn nằm ở chính Ubiquitous Language. Đây là nơi mà một invariant đã được phát biểu rõ:

* Khi có tiến độ đạt được trên một nhiệm vụ (task) của backlog item, thành viên trong nhóm sẽ ước tính số giờ còn lại của task đó.
* Khi một thành viên ước tính rằng số giờ còn lại của một task cụ thể bằng 0, backlog item sẽ kiểm tra lại tất cả các task xem còn giờ tồn đọng nào không. Nếu không còn giờ nào trên bất kỳ task nào, trạng thái của backlog item sẽ tự động được chuyển thành đã xong (done).
* Khi một thành viên ước tính rằng vẫn còn một hoặc nhiều giờ trên một task cụ thể trong khi trạng thái của backlog item vốn đã là done, trạng thái đó sẽ tự động bị thụt lùi (regressed).

Điều này chắc chắn có vẻ như là một invariant thực sự. Trạng thái chính xác của backlog item được tự động điều chỉnh và hoàn toàn phụ thuộc vào tổng số giờ còn lại trên tất cả các task của nó. Nếu tổng số giờ task và trạng thái của backlog item phải luôn nhất quán với nhau, dường như Hình 10.7 đã quy định đúng ranh giới nhất quán của Aggregate. Tuy nhiên, đội ngũ phát triển vẫn nên xác định xem cụm hiện tại có thể phải trả giá những gì xét về mặt hiệu năng và khả năng mở rộng. Chi phí đó sẽ được đặt lên bàn cân so sánh với những gì họ có thể tiết kiệm được nếu trạng thái của backlog item có thể đạt tính nhất quán sau cùng với tổng số giờ task còn lại.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000411_fcf1f3f6e61c4ea65b29364a1d3133b24b607eb8c0c6ab1eb9ef0598a2570cac.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000412_9fcbf7e5d698d47c32176a32dc675079c7a40116c3d74b32b382b900d7ce4f74.png)

Một số người sẽ xem đây là cơ hội kinh điển để áp dụng tính nhất quán sau cùng, nhưng chúng ta sẽ không vội vàng nhảy ngay tới kết luận đó. Hãy cùng phân tích cách tiếp cận dựa trên tính nhất quán giao dịch, sau đó khảo sát những gì có thể đạt được nếu sử dụng tính nhất quán sau cùng. Khi đó, chúng ta có thể tự rút ra kết luận xem phương pháp tiếp cận nào được ưu tiên hơn.

## Ước tính chi phí của Aggregate

Như Hình 10.7 minh họa, mỗi `Task` nắm giữ một tập hợp các instance của `EstimationLogEntry`. Các bản ghi log này mô hình hóa những thời điểm cụ thể khi một thành viên trong nhóm nhập vào một ước lượng mới về số giờ còn lại. Xét về mặt thực tế, mỗi `BacklogItem` sẽ chứa bao nhiêu phần tử `Task`, và một `Task` nhất định sẽ chứa bao nhiêu phần tử `EstimationLogEntry`? Rất khó để nói chính xác. Điều đó phần lớn phụ thuộc vào độ phức tạp của từng task cụ thể và thời gian kéo dài của một sprint. Tuy nhiên, một vài phép tính nhẩm phỏng đoán (back-of-the-envelope - BOTE) có thể giúp ích [Bentley].

Số giờ của task thường được ước tính lại mỗi ngày sau khi một thành viên trong nhóm hoàn thành công việc trên task đó. Giả sử rằng hầu hết các sprint đều kéo dài 2 hoặc 3 tuần. Sẽ có những sprint dài hơn, nhưng khoảng thời gian 2 đến 3 tuần là đủ phổ biến. Vì vậy, chúng ta hãy chọn một số ngày nằm trong khoảng từ 10 đến 15 ngày. Không cần phải quá chính xác, con số 12 ngày là một ước lượng phù hợp vì trên thực tế số lượng sprint 2 tuần có thể nhiều hơn số lượng sprint 3 tuần.