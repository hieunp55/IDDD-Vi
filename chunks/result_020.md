Tiếp theo, hãy xem xét số giờ được phân bổ cho từng task (nhiệm vụ công việc). Cần ghi nhớ rằng các task phải được chia nhỏ thành những đơn vị khả thi để quản lý; thông thường chúng ta áp dụng khoảng thời gian từ 4 đến 16 giờ. Thông thường, nếu một task vượt quá mức ước lượng 12 giờ, các chuyên gia Scrum thường khuyến nghị nên chia nhỏ hơn nữa. Tuy nhiên, việc sử dụng mốc 12 giờ làm phép thử ban đầu sẽ giúp mô phỏng khối lượng công việc phân bổ đồng đều hơn. Ta có thể giả định rằng các task được triển khai 1 giờ mỗi ngày trong suốt 12 ngày của sprint (chu kỳ phát triển ngắn hạn trong Scrum). Cách làm này sẽ tạo điều kiện thuận lợi hơn cho các task phức tạp. Do đó, chúng ta sẽ tính toán 12 lần ước lượng lại (reestimation) cho mỗi task, với giả định ban đầu mỗi task được phân bổ 12 giờ.

Vấn đề đặt ra là: Cần bao nhiêu task cho mỗi backlog item (hạng mục công việc tồn đọng)? Đây cũng là một câu hỏi không dễ trả lời. Sẽ ra sao nếu ta tư duy theo hướng cần từ 2 đến 3 task cho mỗi Layer (tầng kiến trúc) (4) hoặc Hexagonal Port-Adapter (kiến trúc lục giác Cổng - Bộ điều hợp) (4) trên một lát cắt tính năng (feature slice) cụ thể? Chẳng hạn, ta có thể tính 3 task cho User Interface Layer (Tầng giao diện người dùng) (14), 2 task cho Application Layer (Tầng ứng dụng) (14), 3 task cho Domain Layer (Tầng miền nghiệp vụ), và 3 task cho Infrastructure Layer (Tầng hạ tầng) (14). Cách phân bổ này đưa tổng số lên 11 task. Con số này có thể vừa vặn hoặc hơi ít, nhưng vì chúng ta đã chủ ý chọn con số ước lượng task tương đối dồi dào, hãy nâng con số này lên 12 task cho mỗi backlog item để dự trù thoải mái hơn. Như vậy, chúng ta có 12 task, mỗi task có 12 nhật ký ước lượng (estimation log), tương đương tổng cộng 144 đối tượng được thu thập cho mỗi backlog item. Dù con số này có thể cao hơn mức thông thường, nó cung cấp cho chúng ta một phép tính BOTE calculation đủ cụ thể để làm việc.

> 💡 **Giải thích thêm:** BOTE (viết tắt của *Back-Of-The-Envelope calculation*) là thuật ngữ chỉ các phép tính nhẩm nhanh, ước lượng thô sơ mang tính phác thảo (như tính vội trên mặt sau của phong bì thư) nhằm định lượng quy mô vấn đề kỹ thuật trước khi bắt tay đo đạc chi tiết.
> Nguồn tham khảo: [https://en.wikipedia.org/wiki/Back-of-the-envelope_calculation](https://en.wikipedia.org/wiki/Back-of-the-envelope_calculation)

Vẫn còn một biến số khác cần cân nhắc. Nếu khuyến nghị của chuyên gia Scrum về việc chia nhỏ các task được tuân thủ phổ biến, cục diện sẽ thay đổi đôi chút. Việc tăng gấp đôi số lượng task (24) và giảm một nửa số lượng mục nhật ký ước lượng (6) vẫn tạo ra tổng cộng 144 đối tượng. Tuy nhiên, điều này sẽ khiến nhiều task bị tải lên bộ nhớ hơn (24 thay vì 12) trong suốt tất cả các yêu cầu ước lượng, làm tiêu tốn nhiều bộ nhớ hơn cho mỗi yêu cầu. Nhóm phát triển sẽ thử nghiệm nhiều phương án kết hợp khác nhau để xem liệu có bất kỳ tác động đáng kể nào đến các bài kiểm thử hiệu năng hay không. Nhưng trước mắt, họ sẽ bắt đầu với mô hình 12 task, mỗi task 12 giờ.

## Common Usage Scenarios

Bây giờ, việc xem xét các kịch bản sử dụng phổ biến là rất quan trọng. Tần suất một yêu cầu từ người dùng cần nạp đồng thời toàn bộ 144 đối tượng vào bộ nhớ là bao nhiêu? Liệu điều đó có bao giờ xảy ra không? Dường như là không, nhưng nhóm phát triển vẫn cần kiểm tra lại. Nếu không, con số tối đa các đối tượng có khả năng xuất hiện là bao nhiêu? Ngoài ra, liệu có thường xuyên xảy ra tình trạng nhiều client cùng sử dụng gây ra tranh chấp đồng thời (concurrency contention) trên các backlog item hay không? Hãy cùng xem xét.

Các kịch bản sau đây dựa trên việc sử dụng Hibernate (framework ORM cho Java) để thực hiện persistence (lưu trữ dữ liệu bền vững). Đồng thời, mỗi kiểu Entity (thực thể có danh tính định danh) đều sở hữu thuộc tính version phục vụ optimistic concurrency (kiểm soát đồng thời lạc quan) của riêng mình. Cơ chế này hoàn toàn khả thi bởi vì invariant (bất biến nghiệp vụ — điều kiện logic nghiệp vụ luôn phải thỏa mãn) về việc thay đổi trạng thái được quản lý trực tiếp trên Root Entity (Thực thể Gốc) của BacklogItem. Khi trạng thái tự động thay đổi (chuyển sang *done* hoặc quay trở lại *committed*), version của Root Entity sẽ tăng lên. Nhờ đó, các thay đổi đối với các task có thể diễn ra độc lập với nhau mà không tác động đến Root Entity mỗi khi có một task bị chỉnh sửa, trừ phi kết quả của thao tác đó dẫn đến thay đổi trạng thái. (Phân tích dưới đây có thể sẽ cần được đánh giá lại nếu bạn sử dụng các cơ sở dữ liệu dạng tài liệu - document store, bởi vì trên thực tế Root Entity sẽ bị chỉnh sửa mỗi khi một thành phần bên trong nó thay đổi.)

Khi một backlog item vừa được tạo mới, nó không chứa bất kỳ task nào bên trong. Thông thường, phải đến buổi họp lập kế hoạch sprint (sprint planning) thì các task mới được định nghĩa. Trong cuộc họp đó, các task sẽ được cả nhóm xác định. Khi từng task được nêu ra, một thành viên trong nhóm sẽ thêm nó vào backlog item tương ứng. Không hề có lý do gì để hai thành viên phải tranh giành quyền truy cập vào Aggregate (tập hợp các đối tượng nghiệp vụ ràng buộc theo ranh giới nhất quán), giống như đang thi xem ai nhập task mới nhanh hơn. Hành động đó sẽ gây ra xung đột dữ liệu (collision), và một trong hai yêu cầu sẽ thất bại (tương tự như nguyên nhân việc đồng thời thêm các thành phần khác nhau vào Product trước đây từng thất bại). Dù vậy, hai thành viên này có lẽ sẽ sớm nhận ra công việc trùng lặp của họ phản tác dụng đến mức nào.

Nếu các lập trình viên nhận thấy rằng trên thực tế nhiều người dùng thường xuyên muốn cùng lúc thêm các task, điều đó sẽ làm thay đổi đáng kể cục diện phân tích. Nhận thức này có thể ngay lập tức làm nghiêng cán cân về phía việc tách BacklogItem và Task thành hai Aggregate riêng biệt. Mặt khác, đây cũng có thể là thời điểm hoàn hảo để tinh chỉnh cấu hình ánh xạ của Hibernate bằng cách đặt tùy chọn `optimistic-lock` thành `false`. Việc cho phép số lượng task tăng lên đồng thời hoàn toàn có thể hợp lý trong trường hợp này, đặc biệt là nếu chúng không gây ra các vấn đề về hiệu năng và khả năng mở rộng quy mô.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000413_bca29d377b602faa7ae8a2bc71788065a5baec32746f683356a881bb133dd616.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000414_b49bb2aef352733b108a86726b4949f8f0d6184ae78cfb12e6a186aec384ce4c.png)

Nếu ban đầu các task được ước lượng là 0 giờ và sau đó mới được cập nhật thành con số chính xác, chúng ta thường vẫn không gặp phải tình trạng tranh chấp đồng thời, mặc dù việc này sẽ bổ sung thêm một mục nhật ký ước lượng, nâng tổng số tính toán BOTE lên 13. Việc truy cập đồng thời ở đây không làm thay đổi trạng thái của backlog item. Xin nhắc lại, trạng thái chỉ chuyển sang *done* khi số giờ đi từ lớn hơn 0 về 0, hoặc quay ngược về *committed* nếu vốn đã *done* mà số giờ lại bị đổi từ 0 thành 1 hoặc nhiều hơn — đây là hai trường hợp rất hiếm khi xảy ra.

Liệu việc ước lượng hằng ngày có gây ra vấn đề không? Vào ngày đầu tiên của sprint, thông thường sẽ có 0 nhật ký ước lượng trên một task nhất định của backlog item. Đến cuối ngày thứ nhất, mỗi thành viên đảm nhận task đó sẽ giảm bớt 1 giờ ước lượng. Thao tác này bổ sung một nhật ký ước lượng mới cho mỗi task, nhưng trạng thái của backlog item vẫn không bị ảnh hưởng. Hoàn toàn không có xung đột xảy ra trên một task vì chỉ có duy nhất một thành viên phụ trách điều chỉnh giờ của nó. Phải đến ngày thứ 12, chúng ta mới chạm tới ngưỡng chuyển đổi trạng thái. Tuy nhiên, khi mỗi task trong số 11 task bất kỳ được giảm về 0 giờ, trạng thái của backlog item vẫn giữ nguyên. Chỉ duy nhất lần ước lượng cuối cùng — lần thứ 144 trên task thứ 12 — mới kích hoạt việc tự động chuyển đổi trạng thái sang *done*.

Phân tích này đã dẫn nhóm nghiên cứu đến một nhận thức quan trọng. Ngay cả khi họ thay đổi kịch bản sử dụng, tăng tốc độ hoàn thành task lên gấp đôi (6 ngày) hoặc thậm chí xáo trộn hoàn toàn, điều đó cũng không thay đổi được bản chất vấn đề. Luôn luôn là lần ước lượng cuối cùng thực hiện chuyển đổi trạng thái, và chính lần đó mới làm thay đổi Root Entity. Đây dường như là một thiết kế an toàn, mặc dù chi phí bộ nhớ (memory overhead) vẫn còn là một dấu hỏi.

## Memory Consumption

Bây giờ hãy giải quyết vấn đề tiêu thụ bộ nhớ. Điểm cốt lõi ở đây là các ước lượng được ghi lại theo ngày dưới dạng các Value Objects (đối tượng giá trị). Nếu một thành viên ước lượng lại bao nhiêu lần đi chăng nữa trong cùng một ngày, chỉ có giá trị ước lượng gần nhất được giữ lại. Giá trị mới nhất trong cùng ngày sẽ thay thế giá trị trước đó trong tập hợp. Tại thời điểm này, hệ thống không yêu cầu phải theo dõi các sai sót trong quá trình ước lượng task. Chúng ta đang dựa trên giả định rằng một task sẽ không bao giờ có số lượng mục nhật ký ước lượng nhiều hơn số ngày mà sprint đang diễn ra. Giả định này sẽ thay đổi nếu các task được định nghĩa từ một hoặc nhiều ngày trước cuộc họp lập kế hoạch sprint, và số giờ được ước lượng lại vào bất kỳ ngày nào sớm hơn đó. Khi đó sẽ có thêm một nhật ký phụ cho mỗi ngày phát sinh thêm.

Thế còn tổng số lượng task và ước lượng nằm trong bộ nhớ cho mỗi lần ước lượng lại thì sao? Khi áp dụng lazy loading (cơ chế trì hoãn nạp dữ liệu cho đến khi cần thiết) cho các task và các nhật ký ước lượng, chúng ta sẽ có tối đa 12 cộng 12 đối tượng trong tập hợp được đưa vào bộ nhớ tại một thời điểm cho mỗi yêu cầu. Điều này là do toàn bộ 12 task sẽ được nạp khi truy cập vào tập hợp đó. Để thêm mục nhật ký ước lượng mới nhất vào một trong các task này, chúng ta phải nạp tập hợp các mục nhật ký ước lượng của task đó. Thao tác này có thể kéo thêm tối đa 12 đối tượng nữa. Cuối cùng, thiết kế Aggregate này đòi hỏi một backlog item, 12 task và 12 mục nhật ký, tương đương tối đa tổng cộng 25 đối tượng. Con số đó không hề lớn; đây vẫn là một Aggregate nhỏ. Một yếu tố khác là mức chạm ngưỡng tối đa (chẳng hạn 25 đối tượng) chỉ xuất hiện vào ngày cuối cùng của sprint. Trong phần lớn thời gian diễn ra sprint, Aggregate thậm chí còn nhỏ hơn thế nhiều.

Liệu thiết kế này có gây ra các vấn đề về hiệu năng do lazy load hay không? Khả năng là có, bởi vì trên thực tế nó đòi hỏi tới hai lần lazy load: một lần cho danh sách task và một lần cho các mục nhật ký ước lượng của một trong các task đó. Nhóm sẽ phải tiến hành kiểm thử để khảo sát chi phí phụ phát sinh từ các lần nạp dữ liệu liên tiếp này.

Còn một yếu tố nữa. Scrum cho phép các nhóm thử nghiệm để tìm ra mô hình lập kế hoạch phù hợp nhất với thực tiễn của họ. Như được giải thích bởi [Sutherland], các nhóm giàu kinh nghiệm với vận tốc (velocity) ổn định có thể ước lượng bằng story points (điểm câu chuyện) thay vì tính theo giờ của task. Khi định nghĩa từng task, họ có thể chỉ gán 1 giờ cho mỗi task. Trong suốt sprint, họ sẽ chỉ ước lượng lại duy nhất một lần cho mỗi task: chuyển từ 1 giờ về 0 giờ khi task đó hoàn thành. Xét về khía cạnh thiết kế Aggregate, việc sử dụng story point giúp giảm tổng số nhật ký ước lượng cho mỗi task xuống chỉ còn 1 và gần như triệt tiêu hoàn toàn chi phí bộ nhớ.

Sau này, các lập trình viên của ProjectOvation sẽ có thể xác định bằng phương pháp phân tích (trên mức trung bình) xem có bao nhiêu task và mục nhật ký ước lượng thực tế tồn tại trên mỗi backlog item bằng cách khảo sát dữ liệu thực tế trên môi trường production.

Những phân tích phía trên đã đủ để thôi thúc nhóm tiến hành kiểm thử dựa trên các tính toán BOTE của mình. Tuy nhiên, sau khi thu được các kết quả chưa thực sự thuyết phục, họ nhận thấy vẫn còn quá nhiều biến số khiến họ chưa thể an tâm rằng thiết kế này đã giải quyết triệt để các mối lo ngại. Vẫn còn đủ các yếu tố chưa rõ ràng để họ phải cân nhắc đến một phương án thiết kế thay thế.

## Exploring Another Alternative Design

Liệu có một thiết kế nào khác có thể giúp định hình ranh giới Aggregate phù hợp hơn với các kịch bản sử dụng thực tế hay không?

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000415_d6514b2652a481f4b06aa562b27c9fdd694bcaca995db85c87314009647428c2.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000416_d5a2caea8d4a55a871a7e66cd9d15236516e46c0f5e750992c6c1106e5abb3de.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000417_c6b0a13aa93ddc6251fe496703b663c1cdedd89fd2d6ad29b80dd3ec77b45f69.png)

Hình 10.8 BacklogItem và Task được mô hình hóa thành các Aggregate riêng biệt

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000418_f58298c0534be85683303436a7e5ae2ba2357668679c24db6e2010d0e9c23eb3.png)

Để có cái nhìn thấu đáo, nhóm muốn suy xét cẩn thận xem họ sẽ phải làm gì để biến Task thành một Aggregate độc lập, và liệu điều đó có thực sự mang lại lợi ích cho họ hay không. Những gì họ hình dung được thể hiện trong Hình 10.8. Làm như vậy sẽ giảm bớt chi phí cấu thành thành phần (part composition overhead) đi 12 đối tượng và giảm chi phí lazy load. Trên thực tế, thiết kế này mang lại cho họ tùy chọn nạp sẵn (eagerly load) các mục nhật ký ước lượng trong mọi trường hợp nếu cách đó đem lại hiệu năng tốt nhất.

Các lập trình viên đã thống nhất không chỉnh sửa các Aggregate riêng biệt — cả Task lẫn BacklogItem — trong cùng một transaction. Họ cần xác định xem liệu có thể thực hiện việc tự động chuyển đổi trạng thái cần thiết trong một khung thời gian chấp nhận được hay không. Họ sẽ phải chấp nhận giảm bớt tính nhất quán của invariant, bởi vì trạng thái không thể đạt được tính nhất quán ngay trong cùng một transaction. Liệu điều đó có được chấp nhận? Họ đã thảo luận vấn đề này với các chuyên gia nghiệp vụ (domain experts) và biết được rằng việc có một độ trễ nhất định giữa lần ước lượng 0 giờ cuối cùng và thời điểm trạng thái được gán thành *done* (và ngược lại) là hoàn toàn có thể chấp nhận được.

## Implementing Eventual Consistency

Dường như đây là một trường hợp hoàn toàn hợp lý để áp dụng eventual consistency (tính nhất quán cuối cùng) giữa các Aggregate riêng biệt. Dưới đây là cách cơ chế này có thể vận hành.

Khi một Task xử lý command `estimateHoursRemaining()`, nó sẽ publish một Domain Event (sự kiện miền nghiệp vụ) tương ứng. Hiện tại nó đã làm điều đó rồi, nhưng nhóm phát triển giờ đây sẽ tận dụng chính Event này để đạt được eventual consistency. Event này được mô hình hóa với các thuộc tính sau:

```java
public class TaskHoursRemainingEstimated implements DomainEvent {
    private Date occurredOn;
    private TenantId tenantId;
    private BacklogItemId backlogItemId;
    private TaskId taskId;
    private int hoursRemaining;
    ...
}
```

Một subscriber chuyên trách giờ đây sẽ lắng nghe các sự kiện này và ủy quyền cho một Domain Service (dịch vụ miền) để điều phối quá trình xử lý tính nhất quán. Service này sẽ:

* Sử dụng `BacklogItemRepository` để truy xuất `BacklogItem` được chỉ định.
* Sử dụng `TaskRepository` để truy xuất tất cả các thể hiện `Task` liên kết với `BacklogItem` được chỉ định.
* Thực thi command của `BacklogItem` có tên là `estimateTaskHoursRemaining()`, truyền vào thuộc tính `hoursRemaining` của Domain Event và danh sách các thể hiện `Task` đã truy xuất được. `BacklogItem` có thể chuyển đổi trạng thái của nó tùy thuộc vào các tham số này.

Nhóm phát triển nên tìm cách tối ưu hóa quy trình này. Thiết kế ba bước này đòi hỏi tất cả các thể hiện `Task` phải được nạp lên mỗi khi có một thao tác ước lượng lại diễn ra. Nếu dựa trên ước tính BOTE của chúng ta và tiến trình công việc liên tục hướng về trạng thái *done*, thì có tới 143 trên tổng số 144 lần thao tác này là không cần thiết. Vấn đề này có thể được tối ưu hóa khá dễ dàng. Thay vì sử dụng Repository để lấy toàn bộ các thể hiện `Task`, họ chỉ cần yêu cầu nó trả về tổng số giờ còn lại của tất cả các `Task` do cơ sở dữ liệu tính toán:

```java
public class HibernateTaskRepository implements TaskRepository {
    ...
    public int totalBacklogItemTaskHoursRemaining(
            TenantId aTenantId,
            BacklogItemId aBacklogItemId) {
        Query query = session.createQuery(
            "select sum(task.hoursRemaining) from Task task " +
            "where task.tenantId = ? and " +
            "task.backlogItemId = ?");
        ...
    }
}
```

Eventual consistency làm giao diện người dùng trở nên phức tạp hơn đôi chút. Trừ phi việc chuyển đổi trạng thái có thể hoàn tất trong vòng vài trăm mili-giây, nếu không thì giao diện người dùng sẽ hiển thị trạng thái mới như thế nào? Liệu họ có nên đặt logic nghiệp vụ vào view để tự xác định trạng thái hiện tại? Cách làm đó sẽ tạo thành một smart UI anti-pattern (phản mẫu thiết kế đặt logic nghiệp vụ trực tiếp vào giao diện người dùng). Hay có lẽ view sẽ chỉ hiển thị trạng thái cũ (stale status) và để mặc người dùng tự xử lý sự không nhất quán về mặt thị giác đó? Điều này rất dễ bị nhìn nhận là một lỗi phần mềm (bug), hoặc chí ít cũng gây khó chịu lớn cho người dùng.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000419_81afdb9b6f72ed0c9d7b1fbd6fc004d74bdfef1f1c95fbbf6db81b0d1d4f5fde.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000420_f30405abc72177639065d61b2218dfb9699a5ff34eaf2539501a7a689a07080d.png)

View có thể sử dụng một yêu cầu Ajax polling chạy ngầm, nhưng điều đó có thể rất kém hiệu quả. Vì thành phần view không thể dễ dàng xác định chính xác khi nào việc kiểm tra cập nhật trạng thái là cần thiết, phần lớn các yêu cầu ping Ajax sẽ trở nên dư thừa. Nếu áp dụng số liệu BOTE của chúng ta, 143 trên 144 lần ước lượng lại sẽ không làm thay đổi trạng thái, dẫn đến một lượng lớn yêu cầu thừa thãi đổ dồn vào Web tier. Nếu có sự hỗ trợ phù hợp từ phía server, các client thay vào đó có thể dựa vào Comet (còn gọi là Ajax Push). Dù đây là một thử thách thú vị, nó lại đưa vào một công nghệ hoàn toàn mới mà nhóm chưa từng có kinh nghiệm sử dụng.

Mặt khác, có lẽ giải pháp tốt nhất lại chính là giải pháp đơn giản nhất. Họ có thể chọn đặt một chỉ dẫn trực quan trên màn hình để thông báo cho người dùng biết rằng trạng thái hiện tại đang chờ xác nhận. View có thể gợi ý một khoảng thời gian để người dùng quay lại kiểm tra hoặc làm mới trang. Hoặc cách khác là trạng thái đã thay đổi rất có thể sẽ hiển thị trong lần render view tiếp theo. Hướng tiếp cận này an toàn. Nhóm sẽ cần thực hiện một số kiểm thử chấp nhận người dùng (user acceptance tests), nhưng đây là hướng đi đầy triển vọng.

## Is It the Team Member's Job?

Một câu hỏi quan trọng từ nãy đến giờ hoàn toàn bị bỏ quên: Trách nhiệm đồng bộ trạng thái của một backlog item cho nhất quán với toàn bộ số giờ task còn lại thực chất thuộc về ai? Liệu các thành viên trong nhóm Scrum có bận tâm việc trạng thái của backlog item cha chuyển sang *done* ngay khi họ đặt số giờ của task cuối cùng về 0 hay không? Liệu họ có luôn biết rằng mình đang làm việc với task cuối cùng còn giờ hay không? Có thể họ biết, và cũng có thể trách nhiệm của mỗi thành viên là phải đưa từng backlog item đến trạng thái hoàn thành chính thức.

Mặt khác, sẽ ra sao nếu có một bên liên quan (stakeholder) khác tham gia vào dự án? Chẳng hạn, product owner (chủ sở hữu sản phẩm) hoặc một người nào đó có thể muốn kiểm tra backlog item ứng viên xem đã đạt yêu cầu hoàn thành hay chưa. Có thể ai đó muốn chạy thử tính năng trên một máy chủ tích hợp liên tục (continuous integration server) trước. Nếu các bên liên quan hài lòng với xác nhận hoàn thành của các lập trình viên, họ sẽ đánh dấu thủ công trạng thái thành *done*. Tình huống này chắc chắn sẽ làm thay đổi hoàn toàn cuộc chơi, cho thấy rằng cả transactional consistency lẫn eventual consistency đều không thực sự cần thiết. Các task hoàn toàn có thể được tách rời khỏi backlog item cha vì trường hợp sử dụng mới này cho phép điều đó. Tuy nhiên, nếu thực sự chính các thành viên trong nhóm là người kích hoạt quá trình tự động chuyển sang *done*, điều đó đồng nghĩa với việc các task có lẽ nên được cấu thành bên trong backlog item để đảm bảo tính nhất quán theo transaction. Thú vị thay, ở đây cũng không có câu trả lời rõ ràng tuyệt đối, và điều này rất có thể gợi ý rằng đây nên là một cấu hình tùy chọn của ứng dụng.

Việc giữ các task bên trong backlog item của chúng sẽ giải quyết được vấn đề nhất quán, và đó là một lựa chọn mô hình hóa có thể hỗ trợ cả việc chuyển đổi trạng thái tự động lẫn thủ công.

Bài tập giá trị này đã mở ra một khía cạnh hoàn toàn mới của domain. Dường như các nhóm nên có khả năng cấu hình một tùy chọn luồng công việc (workflow preference). Họ sẽ không triển khai tính năng như vậy ngay lúc này, nhưng họ sẽ đưa nó ra để thảo luận sâu hơn. Câu hỏi "đó là trách nhiệm của ai?" đã giúp họ có được một vài nhận thức sống còn về chính domain của mình.

Tiếp theo, một lập trình viên đã đưa ra một gợi ý rất thực tế để thay thế cho toàn bộ quá trình phân tích này. Nếu mối bận tâm hàng đầu của họ là chi phí tiềm tàng của thuộc tính `story`, tại sao không xử lý đích danh thuộc tính đó? Họ có thể giảm tổng dung lượng lưu trữ của `story`, đồng thời tạo thêm một thuộc tính mới mang tên `useCaseDefinition`. Họ có thể thiết kế nó theo kiểu lazy load, bởi vì trong phần lớn thời gian nó sẽ không bao giờ được dùng tới. Hoặc thậm chí họ có thể thiết kế nó thành một Aggregate riêng biệt và chỉ nạp lên khi thực sự cần. Với ý tưởng đó, họ nhận ra đây có thể là thời điểm thích hợp để phá vỡ quy tắc "chỉ tham chiếu các Aggregate bên ngoài thông qua danh tính" (reference external Aggregates only by identity). Việc sử dụng một tham chiếu đối tượng trực tiếp và khai báo ánh xạ quan hệ - đối tượng (ORM) của nó theo kiểu lazy load dường như là một lựa chọn mô hình hóa phù hợp. Có lẽ điều đó là hoàn toàn hợp lý.

## Time for Decisions

Mức độ phân tích chi tiết này không thể kéo dài mãi cả ngày. Cần phải đưa ra một quyết định. Không phải việc đi theo một hướng ở thời điểm hiện tại sẽ triệt tiêu khả năng chọn một lộ trình khác sau này. Sự cởi mở thái quá lúc này đang cản trở tính thực dụng.

Dựa trên tất cả những phân tích này, hiện tại nhóm đang nghiêng về phương án không tách `Task` khỏi `BacklogItem`. Họ không thể chắc chắn rằng việc tách rời nó ngay lúc này có đáng với công sức bỏ thêm, nguy cơ để mặc invariant thực sự không được bảo vệ, hay việc chấp nhận để người dùng có thể gặp phải trạng thái cũ hiển thị trên view hay không. Aggregate hiện tại, theo nhận định của họ, vẫn tương đối nhỏ. Ngay cả khi trường hợp xấu nhất phổ biến phải nạp 50 đối tượng thay vì 25, nó vẫn là một cụm đối tượng có kích thước chấp nhận được. Hiện tại, họ lên kế hoạch xoay quanh đối tượng chuyên biệt lưu trữ định nghĩa use case. Làm như vậy là một thắng lợi nhanh chóng mang lại nhiều lợi ích. Nó tạo ra rất ít rủi ro, vì nó sẽ hoạt động tốt ngay bây giờ và vẫn sẽ hoạt động tốt trong tương lai nếu họ quyết định tách `Task` khỏi `BacklogItem`.

Lựa chọn tách đôi vẫn được giữ lại làm phương án dự phòng. Sau khi tiến hành thêm các thử nghiệm với thiết kế hiện tại, cho chạy qua các bài kiểm thử hiệu năng và chịu tải, cũng như khảo sát sự chấp nhận của người dùng đối với trạng thái eventual consistency, câu trả lời về hướng tiếp cận nào tốt hơn sẽ trở nên rõ ràng hơn. Các con số BOTE hoàn toàn có thể sai nếu trên môi trường production kích thước Aggregate lớn hơn hình dung. Nếu rơi vào trường hợp đó, nhóm chắc chắn sẽ tách nó làm đôi.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000421_f992ed9e93e67e9c8c36abe27f14bd967f9c41ce6bf752a7118663a27546c208.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000422_0617db6b16d520274c31ff8485b24b5228b9eebabffd3dcb7807870bc320f8be.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000423_d79e38c22eb4d65eb67f04897e06b5e3ed5ad1619d04dab796ebb3b151b3a9d3.png)

Nếu là một thành viên của nhóm ProjectOvation, bạn sẽ chọn phương án mô hình hóa nào? Đừng ngần ngại tham gia các buổi khám phá nghiệp vụ như đã được minh họa trong tình huống thực tế này. Toàn bộ nỗ lực đó chỉ mất khoảng 30 phút, hoặc trong trường hợp xấu nhất là 60 phút. Khoảng thời gian đó là hoàn toàn xứng đáng để có được sự thấu hiểu sâu sắc hơn về Core Domain (miền nghiệp vụ cốt lõi) của bạn.

## Implementation

Các yếu tố nổi bật hơn được tóm tắt và nhấn mạnh ở đây có thể giúp việc triển khai trở nên vững chắc hơn, nhưng chúng nên được tìm hiểu kỹ lưỡng hơn trong các chương Entities (5), Value Objects (6), Domain Events (8), Modules (9), Factories (11), và Repositories (12). Hãy sử dụng phần tổng hợp này làm điểm tham chiếu.

## Create a Root Entity with Unique Identity

Hãy mô hình hóa một Entity làm Aggregate Root. Các ví dụ về Root Entity trong các nỗ lực mô hình hóa trước đây là `Product`, `BacklogItem`, `Release`, và `Sprint`. Tùy thuộc vào quyết định tách `Task` khỏi `BacklogItem`, `Task` cũng có thể là một Root.

Mô hình `Product` sau khi tinh chỉnh cuối cùng đã dẫn tới việc khai báo Root Entity như sau:

```java
public class Product extends ConcurrencySafeEntity {
    private Set<ProductBacklogItem> backlogItems;
    private String description;
    private String name;
    private ProductDiscussion productDiscussion;
    private ProductId productId;
    private TenantId tenantId;
    ...
}
```

Lớp `ConcurrencySafeEntity` là một Layer Supertype (siêu kiểu theo tầng — lớp cha chung cho các thực thể trong cùng một tầng kiến trúc) [Fowler, P of EAA] được sử dụng để quản lý surrogate identity (danh tính đại diện / khóa nhân tạo) và kiểm soát phiên bản optimistic concurrency, như đã được giải thích trong chương Entities (5).

Một tập hợp `Set` gồm các thể hiện `ProductBacklogItem` vốn chưa từng được thảo luận trước đây đã được thêm vào Root Entity, có vẻ khá bí ẩn. Việc này phục vụ một mục đích đặc biệt. Nó không giống với tập hợp `BacklogItem` từng được cấu thành ở đây trước đó. Mục đích của nó là để duy trì một thứ tự sắp xếp riêng biệt cho các backlog item.

Mỗi Root Entity phải được thiết kế với một định danh duy nhất trên phạm vi toàn cục (globally unique identity). `Product` đã được mô hình hóa với một kiểu Value mang tên `ProductId`. Kiểu đó là định danh đặc thù của domain (domain-specific identity), và nó khác với surrogate identity do `ConcurrencySafeEntity` cung cấp. Cách thức một định danh dựa trên mô hình được thiết kế, cấp phát và duy trì ra sao sẽ được giải thích sâu hơn trong chương Entities (5). Việc triển khai `ProductRepository` sử dụng phương thức `nextIdentity()` để sinh `ProductId` dưới dạng một UUID (chuỗi định danh duy nhất toàn cục):

```java
public class HibernateProductRepository implements ProductRepository {
    ...
    public ProductId nextIdentity() {
        return new ProductId(java.util.UUID.randomUUID()
            .toString().toUpperCase());
    }
    ...
}
```

Bằng cách sử dụng `nextIdentity()`, một Application Service (dịch vụ tầng ứng dụng) phía client có thể khởi tạo một `Product` với định danh duy nhất toàn cầu của nó:

```java
public class ProductService ... {
    ...
    @Transactional
    public String newProduct(
            String aTenantId,
            String aProductName,
            String aProductDescription) {
        Product product = new Product(
            new TenantId(aTenantId),
            this.productRepository.nextIdentity(),
            "My Product",
            "This is the description of my product.",
            new ProductDiscussion(
                new DiscussionDescriptor(DiscussionDescriptor.UNDEFINED_ID),
                DiscussionAvailability.NOT_REQUESTED));
        this.productRepository.add(product);
        return product.productId().id();
    }
    ...
}
```

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000424_bd64014cfa7fc78c120d694929aa98ffb5ecd83b5298a5b583d45db35acce2fc.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000425_befb1ff97a111fc41500573170e3d787dda115f8d9718523584022c9675aeab9.png)

Application Service sử dụng `ProductRepository` để vừa tạo ra một định danh, vừa tiến hành lưu trữ bền vững (persist) thể hiện `Product` mới đó. Nó trả về biểu diễn dạng `String` thuần túy của `ProductId` mới.

## Favor Value Object Parts

Hãy ưu tiên mô hình hóa một thành phần trực thuộc Aggregate dưới dạng một Value Object thay vì một Entity bất cứ khi nào có thể. Một thành phần bên trong có thể được thay thế hoàn toàn — nếu việc thay thế nó không gây ra chi phí đáng kể trong mô hình hoặc hạ tầng — chính là ứng viên sáng giá nhất.

Mô hình `Product` hiện tại của chúng ta được thiết kế với hai thuộc tính đơn giản và ba thuộc tính có kiểu Value Object. Cả `description` và `name` đều là các thuộc tính `String` có thể bị thay thế hoàn toàn. Các Value `productId` và `tenantId` được duy trì dưới dạng các định danh bất biến; nghĩa là chúng không bao giờ bị thay đổi sau khi khởi tạo. Chúng hỗ trợ việc tham chiếu bằng định danh thay vì tham chiếu trực tiếp đến đối tượng. Trên thực tế, Aggregate `Tenant` được tham chiếu thậm chí còn không nằm trong cùng một Bounded Context (ngữ cảnh giới hạn — ranh giới rõ ràng mà trong đó mô hình miền áp dụng), và do đó chỉ nên được tham chiếu thông qua định danh. Thuộc tính `productDiscussion` là một thuộc tính kiểu Value đạt được sự nhất quán cuối cùng. Khi `Product` được khởi tạo lần đầu, thảo luận có thể được yêu cầu nhưng sẽ chưa tồn tại ngay cho đến một thời điểm sau đó. Nó phải được tạo ra trong Collaboration Context. Một khi quá trình tạo hoàn tất ở Bounded Context kia, định danh và trạng thái mới được thiết lập trên `Product`.

Có những lý do xác đáng giải thích tại sao `ProductBacklogItem` lại được mô hình hóa dưới dạng một Entity thay vì một Value. Như đã thảo luận trong chương Value Objects (6), do cơ sở dữ liệu nền tảng được thao tác qua Hibernate, nó buộc phải mô hình hóa các tập hợp Value dưới dạng các thực thể cơ sở dữ liệu. Việc sắp xếp lại thứ tự của bất kỳ phần tử nào cũng có thể khiến một lượng lớn, thậm chí là toàn bộ các thể hiện `ProductBacklogItem` bị xóa và thay thế lại. Điều đó thường dẫn đến chi phí rất lớn trong tầng hạ tầng. Khi là một Entity, nó cho phép thuộc tính thứ tự được thay đổi trên bất kỳ và toàn bộ các phần tử trong tập hợp thường xuyên theo ý muốn của product owner. Tuy nhiên, nếu chúng ta chuyển từ việc dùng Hibernate với MySQL sang một cơ sở dữ liệu key-value, chúng ta có thể dễ dàng thay đổi `ProductBacklogItem` thành một kiểu Value Object. Khi sử dụng kho lưu trữ key-value hoặc document store, các thể hiện Aggregate thường được serialize thành một biểu diễn giá trị duy nhất để lưu trữ.

## Using Law of Demeter and Tell, Don't Ask

Cả Law of Demeter (Định luật Demeter / nguyên lý biết ít nhất) [Appleton, LoD] lẫn Tell, Don't Ask (Nguyên tắc "Hãy ra lệnh, đừng hỏi") [PragProg, TDA] đều là các nguyên lý thiết kế có thể áp dụng khi triển khai Aggregate, và cả hai đều nhấn mạnh vào việc che giấu thông tin (information hiding). Hãy xem xét các nguyên lý chỉ đạo cấp cao để thấy được lợi ích mà chúng mang lại:

* Law of Demeter: Hướng dẫn này nhấn mạnh vào nguyên lý tri thức tối thiểu (principle of least knowledge). Hãy hình dung một đối tượng client và một đối tượng khác mà client sử dụng để thực thi một hành vi hệ thống nào đó; hãy gọi đối tượng thứ hai là server. Khi đối tượng client sử dụng đối tượng server, nó chỉ nên biết càng ít càng tốt về cấu trúc của server. Các thuộc tính và đặc tính của server — hình thái (shape) của nó — nên được giữ hoàn toàn ẩn giấu đối với client. Client có thể yêu cầu server thực hiện một command được khai báo trên giao diện bề mặt của nó. Tuy nhiên, client tuyệt đối không được thò tay vào bên trong server, đòi hỏi server cung cấp một thành phần nội bộ nào đó, rồi lại thực thi một command trên chính thành phần đó. Nếu client cần một dịch vụ do các thành phần nội bộ của server cung cấp, client không được phép cấp quyền truy cập vào các thành phần bên trong đó để yêu cầu hành vi. Thay vào đó, server chỉ nên cung cấp một giao diện bề mặt và khi được gọi, tự nó sẽ ủy quyền cho các thành phần nội bộ thích hợp để đáp ứng giao diện đó.

Dưới đây là tóm tắt cơ bản về Định luật Demeter: Một phương thức bất kỳ trên một đối tượng chỉ được phép gọi các phương thức thuộc các đối tượng sau: (1) chính nó, (2) bất kỳ tham số nào được truyền vào cho nó, (3) bất kỳ đối tượng nào do chính nó khởi tạo, (4) các đối tượng thành phần trực thuộc mà nó có thể truy cập trực tiếp.

* Tell, Don't Ask: Hướng dẫn này chỉ đơn giản khẳng định rằng các đối tượng nên được ra lệnh phải làm gì. Phần "Don't Ask" (Đừng hỏi) áp dụng cho client như sau: Một đối tượng client không nên hỏi đối tượng server về các thành phần bên trong của nó, rồi tự đưa ra quyết định dựa trên trạng thái nhận được, sau đó mới bắt đối tượng server phải làm điều gì đó. Thay vào đó, client nên "Tell" (Ra lệnh) cho server biết cần phải làm gì, thông qua một command trên public interface của server. Hướng dẫn này có mục đích rất tương đồng với Định luật Demeter, nhưng Tell, Don't Ask có thể dễ áp dụng rộng rãi hơn.

Dựa trên các hướng dẫn này, hãy xem cách chúng ta áp dụng hai nguyên lý thiết kế trên vào `Product`:

```java
public class Product extends ConcurrencySafeEntity {
    ...
    public void reorderFrom(BacklogItemId anId, int anOrdering) {
        for (ProductBacklogItem pbi : this.backlogItems()) {
            pbi.reorderFrom(anId, anOrdering);
        }
    }

    public Set<ProductBacklogItem> backlogItems() {
        return this.backlogItems;
    }
    ...
}
```

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000426_d43800d4796694fa9b384ddc67f10ac1a4d4d2bafc670704015146f66f88d5d2.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000427_848c188c07fab64cd2e1024e5b9155344c34cd92e2982c92a970ecdf77c28e8a.png)

`Product` yêu cầu các client phải sử dụng phương thức `reorderFrom()` của nó để thực thi một command làm thay đổi trạng thái bên trong tập hợp `backlogItems` trực thuộc. Đó là một sự áp dụng chuẩn mực các hướng dẫn trên. Tuy nhiên, phương thức `backlogItems()` cũng có phạm vi `public`. Liệu điều này có phá vỡ các nguyên lý mà chúng ta đang cố gắng tuân thủ bằng cách làm lộ các thể hiện `ProductBacklogItem` ra cho client không? Đúng là nó làm lộ tập hợp, nhưng các client chỉ có thể sử dụng các thể hiện đó để truy vấn thông tin từ chúng. Do public interface của `ProductBacklogItem` bị giới hạn, client không thể nắm bắt được cấu trúc hình thái của `Product` thông qua việc điều hướng sâu vào bên trong. Client chỉ được cung cấp tri thức tối thiểu (least knowledge). Xét theo góc độ của client, các thể hiện tập hợp được trả về có thể chỉ được tạo ra cho một thao tác duy nhất đó và có thể không đại diện cho bất kỳ trạng thái xác định nào của `Product`. Client không bao giờ có thể thực thi các command làm thay đổi trạng thái trên các thể hiện của `ProductBacklogItem`, đúng như phần triển khai của nó đã chỉ rõ:

```java
public class ProductBacklogItem extends ConcurrencySafeEntity {
    ...
    protected void reorderFrom(BacklogItemId anId, int anOrdering) {
        if (this.backlogItemId().equals(anId)) {
            this.setOrdering(anOrdering);
        } else if (this.ordering() >= anOrdering) {
            this.setOrdering(this.ordering() + 1);
        }
    }
    ...
}
```

Hành vi làm thay đổi trạng thái duy nhất của nó được khai báo dưới dạng một phương thức ẩn, có phạm vi truy cập `protected`. Nhờ đó, các client không thể nhìn thấy hay chạm tới command này. Xét trên mọi phương diện thực tế, chỉ có `Product` mới có thể nhìn thấy và thực thi command đó. Client chỉ có thể sử dụng phương thức command public `reorderFrom()` của `Product`. Khi được gọi, `Product` sẽ ủy quyền cho tất cả các thể hiện `ProductBacklogItem` nội bộ bên trong nó thực hiện các sửa đổi bên trong.

Việc triển khai `Product` giúp giới hạn tri thức về chính nó, dễ kiểm thử hơn và dễ bảo trì hơn, tất cả là nhờ vào việc áp dụng các nguyên lý thiết kế đơn giản này.

Bạn sẽ cần phải cân nhắc các lực tác động đối nghịch giữa việc sử dụng Định luật Demeter và Tell, Don't Ask. Chắc chắn rằng cách tiếp cận của Định luật Demeter mang tính hạn chế khắt khe hơn nhiều, ngăn cấm mọi sự điều hướng vào các thành phần của Aggregate vượt ra ngoài phạm vi Root Entity. Mặt khác, việc áp dụng Tell, Don't Ask cho phép điều hướng vượt ra ngoài Root Entity nhưng lại quy định rõ ràng rằng quyền chỉnh sửa trạng thái của Aggregate thuộc về chính Aggregate đó chứ không phải client. Do đó, bạn có thể thấy Tell, Don't Ask là một cách tiếp cận có khả năng ứng dụng rộng rãi hơn trong việc triển khai Aggregate.

## Optimistic Concurrency

Tiếp theo, chúng ta cần xem xét nên đặt thuộc tính version phục vụ optimistic concurrency ở đâu. Khi suy ngẫm về định nghĩa của Aggregate, dường như giải pháp an toàn nhất là chỉ đánh version cho duy nhất Root Entity. Version của Root sẽ được tăng lên mỗi khi một command làm biến đổi trạng thái được thực thi ở bất kỳ đâu bên trong ranh giới Aggregate, bất kể sâu đến mức nào. Áp dụng vào ví dụ xuyên suốt, `Product` sẽ có một thuộc tính version, và khi bất kỳ phương thức command nào như `describeAs()`, `initiateDiscussion()`, `rename()`, hay `reorderFrom()` được thực thi, version sẽ luôn được tăng lên. Điều này sẽ ngăn chặn bất kỳ client nào khác sửa đổi đồng thời bất kỳ thuộc tính hay đặc tính nào ở bất cứ đâu bên trong cùng một `Product`. Tuy nhiên, tùy thuộc vào thiết kế Aggregate cụ thể, điều này có thể rất khó quản lý, và thậm chí là không cần thiết.

Giả định chúng ta đang sử dụng Hibernate, khi tên hoặc mô tả của `Product` bị chỉnh sửa, hoặc thuộc tính `productDiscussion` được gắn vào, version sẽ tự động được tăng lên. Đó là điều hiển nhiên, bởi vì những thành phần đó được nắm giữ trực tiếp bởi Root Entity. Tuy nhiên, làm thế nào để đảm bảo rằng version của `Product` sẽ tăng lên khi bất kỳ mục nào trong `backlogItems` của nó được sắp xếp lại thứ tự? Trên thực tế, chúng ta không thể, hoặc ít nhất là không thể làm điều đó một cách tự động. Hibernate sẽ không coi việc chỉnh sửa một thể hiện thành phần `ProductBacklogItem` là sự chỉnh sửa đối với chính `Product`. Để giải quyết vấn đề này, có lẽ chúng ta chỉ việc thay đổi phương thức `reorderFrom()` của `Product`, đánh dấu dirty cho một cờ nào đó hoặc tự mình tăng version lên:

```java
public class Product extends ConcurrencySafeEntity {
    ...
    public void reorderFrom(BacklogItemId anId, int anOrdering) {
        for (ProductBacklogItem pbi : this.backlogItems()) {
            pbi.reorderFrom(anId, anOrdering);
        }
        this.version(this.version() + 1);
    }
    ...
}
```

Một vấn đề là đoạn mã này luôn luôn làm dirty `Product`, ngay cả khi command sắp xếp lại thứ tự thực tế không tạo ra bất kỳ thay đổi nào. Hơn nữa, đoạn mã này làm rò rỉ các mối bận tâm về mặt hạ tầng vào trong mô hình, vốn là một lựa chọn mô hình hóa miền kém mong muốn nếu có thể tránh được. Chúng ta còn có thể làm gì khác?

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000428_cbfcdd791b890e42de17eda351205802241631d66facede7d6377defdc4adb52.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000429_d75e53208804c29f78cbf4ff2e1d1cf1db00458f66058c2dc9986209cab002ca.png)

## Cowboy Logic

AJ: "Tôi đang nghĩ hôn nhân cũng là một dạng optimistic concurrency. Khi một người đàn ông lấy vợ, anh ta lạc quan tin rằng cô ấy sẽ không bao giờ thay đổi. Và cùng lúc đó, cô ấy lại lạc quan tin rằng mình sẽ thay đổi được anh ta."

> 💡 **Giải thích thêm:** "Cowboy Logic" là các mẩu đối thoại trào phúng, hài hước mang phong cách miền viễn Tây được Vaughn Vernon lồng ghép vào sách. Ở đây, tác giả ví von hôn nhân với cơ chế "kiểm soát đồng thời lạc quan" (optimistic concurrency): cả hai bên đều hành động dựa trên giả định lạc quan rằng phía bên kia sẽ vận hành theo kỳ vọng của mình mà không xung đột, nhưng thực tế khi commit thì va chạm thường xuyên xảy ra.
> (Không có nguồn trích dẫn xác thực — cần tự kiểm chứng thêm)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000430_bee728976b7499f5aa2eee8b9cc02b405deacad14bc8360004923b1029d063ac.png)

Trên thực tế, trong trường hợp của `Product` và các thể hiện `ProductBacklogItem` của nó, rất có thể chúng ta không cần phải chỉnh sửa version của Root khi có bất kỳ `backlogItems` nào bị sửa đổi. Do các thể hiện trong tập hợp bản thân chúng đã là các Entity, chúng hoàn toàn có thể tự mang thuộc tính version optimistic concurrency của riêng mình. Nếu hai client cùng sắp xếp lại bất kỳ thể hiện `ProductBacklogItem` nào trùng nhau, client commit thay đổi sau cùng sẽ bị thất bại. Phải thừa nhận rằng việc sắp xếp lại thứ tự bị trùng lặp này hiếm khi, thậm chí không bao giờ xảy ra, bởi vì thông thường chỉ có product owner mới là người sắp xếp lại các hạng mục trong product backlog.

Việc đánh version cho tất cả các thành phần Entity không phải lúc nào cũng mang lại hiệu quả trong mọi trường hợp. Đôi khi, cách duy nhất để bảo vệ một invariant là phải sửa đổi version của Root Entity. Điều này có thể được thực hiện dễ dàng hơn nếu chúng ta có thể sửa đổi một thuộc tính hợp lệ trên chính Root Entity. Trong trường hợp này, thuộc tính của Root sẽ luôn được sửa đổi nhằm phản hồi lại sự thay đổi của một thành phần nằm sâu hơn bên trong, từ đó khiến Hibernate tự động tăng version của Root. Hãy nhớ lại rằng cách tiếp cận này đã được mô tả trước đó để mô hình hóa việc thay đổi trạng thái trên `BacklogItem` khi tất cả các thể hiện `Task` của nó đã chuyển về 0 giờ còn lại.

Tuy nhiên, cách tiếp cận đó có thể không khả thi trong mọi trường hợp. Nếu không, chúng ta có thể bị cám dỗ tìm đến các hook do cơ chế persistence cung cấp để dirty Root một cách thủ công khi Hibernate phát hiện một thành phần bên trong bị sửa đổi. Việc này sẽ kéo theo nhiều vấn đề phức tạp. Nó thường chỉ có thể vận hành được bằng cách duy trì các mối quan hệ hai chiều (bidirectional associations) giữa các thành phần con và Root cha. Mối quan hệ hai chiều này cho phép điều hướng ngược từ con về Root khi Hibernate gửi một sự kiện vòng đời (life cycle event) tới một listener chuyên biệt. Dù vậy, đừng quên rằng [Evans] thường không khuyến khích việc sử dụng quan hệ hai chiều trong hầu hết các trường hợp. Điều này càng đúng hơn nếu chúng chỉ được duy trì đơn thuần để đối phó với optimistic concurrency — vốn chỉ là một mối bận tâm thuộc về tầng hạ tầng.

Mặc dù chúng ta không muốn các mối bận tâm về hạ tầng chi phối các quyết định mô hình hóa, chúng ta vẫn có thể có động lực để chọn một con đường ít đau đớn hơn. Khi việc sửa đổi Root Entity trở nên quá khó khăn và tốn kém, đó có thể là một dấu hiệu rõ ràng cho thấy chúng ta cần chia nhỏ các Aggregate của mình chỉ còn lại một Root Entity duy nhất, chỉ chứa các thuộc tính đơn giản và các đặc tính kiểu Value Object. Khi Aggregate chỉ bao gồm một Root Entity duy nhất, Root sẽ luôn luôn bị sửa đổi mỗi khi có bất kỳ thành phần nào của nó thay đổi.

Cuối cùng, cần phải thừa nhận rằng các kịch bản nêu trên hoàn toàn không phải là vấn đề khi toàn bộ một Aggregate được lưu trữ bền vững dưới dạng một giá trị duy nhất (single value) và chính giá trị đó tự ngăn chặn xung đột đồng thời. Hướng tiếp cận này có thể được tận dụng khi sử dụng MongoDB, Riak, lưới phân tán Coherence của Oracle, hoặc GemFire của VMware. Chẳng hạn, khi một Aggregate Root triển khai interface `Versionable` của Coherence và Repository của nó sử dụng bộ xử lý mục nhập `VersionedPut`, Root sẽ luôn là đối tượng duy nhất được dùng để phát hiện xung đột đồng thời. Các kho lưu trữ key-value khác cũng có thể cung cấp các tiện ích tương tự.

## Avoid Dependency Injection

Việc tiêm phụ thuộc (Dependency Injection) một Repository hoặc Domain Service vào bên trong một Aggregate nhìn chung nên được coi là một hành vi có hại. Động cơ của việc này có thể là để tra cứu một thể hiện đối tượng phụ thuộc ngay từ bên trong Aggregate. Đối tượng phụ thuộc đó có thể là một Aggregate khác, hoặc một tập hợp nhiều Aggregate. Như đã nêu trước đó trong mục "Quy tắc: Tham chiếu các Aggregate khác bằng định danh", tốt nhất là các đối tượng phụ thuộc nên được tra cứu từ trước khi phương thức command của Aggregate được gọi, rồi truyền đối tượng đó vào phương thức. Việc sử dụng Disconnected Domain Model (mô hình miền ngắt kết nối) nhìn chung là một hướng tiếp cận kém tối ưu hơn.

Ngoài ra, trong một domain có lưu lượng truy cập cực cao, khối lượng dữ liệu khổng lồ và đòi hỏi hiệu năng tối đa, nơi bộ nhớ và chu kỳ thu gom rác (garbage collection) bị quá tải nặng nề, hãy nghĩ đến chi phí tiềm tàng của việc inject các thể hiện Repository và Domain Service vào các Aggregate. Việc đó sẽ đòi hỏi thêm bao nhiêu tham chiếu đối tượng dư thừa? Một số người có thể lập luận rằng mức độ đó chưa đủ để làm quá tải môi trường vận hành của họ, nhưng môi trường của họ có lẽ không thuộc dạng domain đang được mô tả ở đây. Dù vậy, hãy hết sức cẩn trọng để không bổ sung thêm các chi phí không cần thiết vốn có thể dễ dàng tránh được bằng cách áp dụng các nguyên lý thiết kế khác — chẳng hạn như tra cứu các dependency trước khi gọi phương thức command của Aggregate rồi truyền chúng vào.

Khuyến cáo này chỉ nhằm cảnh báo việc inject Repository và Domain Service vào các thể hiện Aggregate. Dĩ nhiên, Dependency Injection hoàn toàn phù hợp cho rất nhiều tình huống thiết kế khác. Chẳng hạn, việc inject các tham chiếu Repository và Domain Service vào các Application Service là vô cùng hữu ích.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000431_93befbcf4af5074dfde9741a907868f34cd1428c666390a46b258648de7872cb.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000432_3b343d32c3bec45b486c52f13787787d2508f29dc61472bd81c3344e3db0a93a.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000433_881f4be078c88636ccf75d6188bb37bf260a529a9e182bae5152961d266c9f28.png)

## Wrap-Up

Chúng ta đã nghiên cứu tầm quan trọng sống còn của việc tuân thủ các Quy tắc ngón tay cái về Aggregate (Aggregate Rules of Thumb) khi thiết kế Aggregate.

* Bạn đã chứng kiến những hệ quả tiêu cực của việc mô hình hóa các Aggregate dạng cụm lớn (large-cluster Aggregates).
* Bạn đã học được cách mô hình hóa các invariant thực sự bên trong các ranh giới nhất quán (consistency boundaries).
* Bạn đã cân nhắc những lợi thế của việc thiết kế các Aggregate có kích thước nhỏ.
* Giờ đây bạn đã hiểu lý do tại sao nên ưu tiên việc tham chiếu các Aggregate khác thông qua định danh.
* Bạn đã khám phá tầm quan trọng của việc áp dụng eventual consistency bên ngoài ranh giới Aggregate.
* Bạn đã thấy nhiều kỹ thuật triển khai khác nhau, bao gồm cả cách áp dụng các nguyên tắc Tell, Don't Ask và Law of Demeter.

Nếu chúng ta tuân thủ nghiêm ngặt các quy tắc này, chúng ta sẽ có được tính nhất quán ở những nơi thực sự cần thiết, đồng thời hỗ trợ xây dựng các hệ thống có hiệu năng tối ưu và khả năng mở rộng quy mô vượt trội, trong khi vẫn nắm bắt trọn vẹn Ubiquitous Language (ngôn ngữ chung thống nhất của dự án) của miền nghiệp vụ thông qua một mô hình được thiết kế tỉ mỉ.

## Chapter 11

## Factories

"Tôi không thể chịu nổi sự xấu xí trong các nhà máy! Nào, chúng ta vào trong thôi! Nhưng hãy cẩn thận đấy, các cô cậu bé yêu quý của tôi! Đừng có mất bình tĩnh! Đừng quá phấn khích! Phải hết sức bình tĩnh!" - Willy Wonka

> 💡 **Giải thích thêm:** Câu trích dẫn kinh điển của nhân vật Willy Wonka trong tác phẩm thiếu nhi nổi tiếng *Charlie and the Chocolate Factory* (Charlie và nhà máy sô-cô-la) của Roald Dahl. Tác giả mượn hình ảnh "nhà máy" đầy nhiệm màu nhưng đòi hỏi sự trật tự, sạch sẽ của Wonka để chơi chữ với mẫu thiết kế "Factory" (nhà máy khởi tạo đối tượng) trong kỹ thuật phần mềm: việc tạo đối tượng phải gọn gàng, tránh sự lộn xộn, xấu xí (ugliness) và cần kiểm soát tốt sự phức tạp.
> Nguồn tham khảo: [https://en.wikipedia.org/wiki/Charlie_and_the_Chocolate_Factory](https://en.wikipedia.org/wiki/Charlie_and_the_Chocolate_Factory)

Trong số tất cả các pattern được sử dụng trong DDD, Factory (nhà máy khởi tạo đối tượng) có lẽ là một trong những pattern được biết đến nhiều nhất. Những mẫu thiết kế được quảng bá rộng rãi trong cuốn *Design Patterns* [Gamma et al.] gồm có Abstract Factory (nhà máy trừu tượng), Factory Method (phương thức nhà máy), và Builder (mẫu xây dựng từng bước). Tôi hoàn toàn không có ý định làm lu mờ những lời khuyên đã được đưa ra trong tài liệu đó, cũng như những chỉ dẫn do [Evans] cung cấp. Trọng tâm ở đây là mang đến cho bạn các ví dụ về cách thức ứng dụng Factory trong mô hình miền (domain model).

## Road Map to This Chapter

* Tìm hiểu lý do tại sao việc sử dụng Factory có thể tạo ra các mô hình giàu tính biểu đạt và bám sát Ubiquitous Language (1).
* Xem cách SaaSOvation sử dụng Factory Method như những hành vi của Aggregate (10).
* Cân nhắc cách sử dụng Factory Method để tạo ra các thể hiện Aggregate thuộc các kiểu khác.
* Tìm hiểu cách thiết kế Domain Service đóng vai trò là các Factory trong khi tương tác với các Bounded Context (2) khác và chuyển đổi các đối tượng ngoại lai sang các kiểu nội bộ của hệ thống.

## Factories in the Domain Model

Hãy xem xét những động lực chính thôi thúc việc sử dụng Factory:

> Chuyển giao trách nhiệm khởi tạo các thể hiện của các đối tượng phức tạp và các AGGREGATE cho một đối tượng riêng biệt; bản thân đối tượng này có thể không mang trách nhiệm nghiệp vụ nào trong mô hình miền nhưng vẫn là một phần của thiết kế miền. Cung cấp một interface đóng gói toàn bộ quá trình lắp ráp phức tạp mà không đòi hỏi client phải tham chiếu đến các lớp cụ thể của đối tượng đang được khởi tạo. Tạo ra toàn bộ các AGGREGATE như một khối hoàn chỉnh, đồng thời thực thi nghiêm ngặt các invariant của chúng. [Evans, tr. 138]

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000434_ad0475f3b890075af21606c2b3d7a70cc1ab352b68c4bee07849a1851c7eac1a.png)

Một Factory có thể có hoặc không có các trách nhiệm bổ sung khác trong mô hình miền ngoài việc khởi tạo đối tượng. Một đối tượng chỉ có mục đích duy nhất là khởi tạo một kiểu Aggregate cụ thể sẽ không có trách nhiệm nào khác và thậm chí sẽ không được coi là một công dân hạng nhất (first-class citizen) của mô hình. Nó chỉ đơn thuần là một Factory. Một Aggregate Root cung cấp một Factory Method để sản sinh ra các thể hiện của một kiểu Aggregate khác (hoặc các thành phần nội bộ) sẽ mang trách nhiệm chính là cung cấp các hành vi cốt lõi của Aggregate đó, và Factory Method chỉ là một trong số các hành vi đó mà thôi.

Trường hợp thứ hai chính là tình huống xuất hiện thường xuyên hơn trong các ví dụ của tôi. Các Aggregate mà tôi minh họa phần lớn đều có cấu trúc khởi tạo không quá phức tạp. Tuy nhiên, một số chi tiết quan trọng trong quá trình khởi tạo Aggregate vẫn phải được bảo vệ cẩn mật để tránh tạo ra trạng thái sai lệch. Hãy xem xét các yêu cầu của một môi trường multitenancy (kiến trúc đa người thuê / đa khách hàng). Nếu một thể hiện Aggregate bị tạo nhầm dưới một tenant khác, bị gán sai `TenantId`, hậu quả có thể sẽ rất thảm khốc. Chúng ta phải chịu trách nhiệm rất cao trong việc giữ cho dữ liệu của từng tenant được phân tách biệt lập và an toàn tuyệt đối trước mọi tenant khác. Việc đặt một Factory Method được thiết kế cẩn trọng trên các Aggregate Root cụ thể có thể đảm bảo rằng thông tin tenant và các định danh liên kết khác luôn được tạo ra một cách chính xác. Nó đơn giản hóa phía client, chỉ yêu cầu client truyền vào các tham số cơ bản — thường chỉ là các Value Objects (6) — bằng cách che giấu hoàn toàn các chi tiết khởi tạo phức tạp khỏi tầm mắt của client.

Hơn nữa, các Factory Method đặt trên các Aggregate cho phép bạn biểu đạt Ubiquitous Language theo những cách mà các constructor đơn thuần không thể làm được. Khi tên của phương thức hành vi mang tính biểu đạt cao xét theo góc độ của Ubiquitous Language, bạn đã có thêm một lý do vô cùng thuyết phục để sử dụng Factory Method.

## Cowboy Logic

* LB: "Tôi từng làm việc trong một nhà máy sản xuất trụ nước cứu hỏa. Bạn chẳng thể nào đỗ xe ở bất kỳ chỗ nào gần nơi đó cả."

> 💡 **Giải thích thêm:** Đây là một câu đùa chơi chữ đặc trưng của văn hóa Mỹ: "fire hydrant" (trụ nước cứu hỏa trên vỉa hè) là khu vực bị pháp luật cấm đỗ xe tuyệt đối trong bán kính quy định. Vì vậy, một nhà máy sản xuất toàn trụ cứu hỏa thì hiển nhiên xung quanh sẽ cấm đỗ xe trên mọi nẻo đường.
> (Không có nguồn trích dẫn xác thực — cần tự kiểm chứng thêm)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000435_b6e7ec98335670b6f93ec9ed379a0b8611f84eef38591e46b54b36e20ac0ab2c.png)

Các Bounded Context mẫu trong một số trường hợp quả thực đòi hỏi việc khởi tạo phức tạp. Những tình huống này xuất hiện khi chúng ta Tích hợp các Bounded Context (Integrating Bounded Contexts) (13). Vào những thời điểm đó, các Services (7) sẽ đóng vai trò là các Factory tạo ra các Aggregate hoặc Value Object thuộc nhiều kiểu khác nhau.

Một trường hợp mà bạn sẽ thấy Abstract Factory mang lại lợi ích to lớn là khi tạo ra các đối tượng thuộc các kiểu khác nhau trong một hệ thống phân cấp lớp (class hierarchy), vốn là một trường hợp sử dụng kinh điển. Phía client chỉ cần truyền vào một số tham số cơ bản, từ đó Factory có thể tự xác định kiểu cụ thể nào bắt buộc phải được tạo ra. Trong số các ví dụ của mình, tôi không có bất kỳ hệ thống phân cấp lớp đặc thù cho domain nào, vì vậy tôi sẽ không minh họa cách sử dụng này ở đây. Nếu bạn bắt gặp các hệ thống phân cấp lớp trong các nỗ lực mô hình hóa miền tương lai của mình, tôi khuyên bạn nên xem qua phần thảo luận liên quan trong chương Repositories (12). Nó sẽ giúp bạn bước vào công việc đó với một đôi mắt tỉnh táo và sáng suốt. Nếu bạn quyết định sử dụng các hệ thống phân cấp lớp trong thiết kế của mình, hãy chuẩn bị sẵn tinh thần cho những nỗi đau đớn tiềm tàng có thể phát sinh.

## Factory Method on Aggregate Root

Xuyên suốt ba Bounded Context mẫu, có rất nhiều vị trí đặt Factory trên các Entity đóng vai trò là Aggregate Root, và Bảng 11.1 cung cấp một bản tổng hợp về chúng.

Tôi thảo luận về các Factory Method của `Product` trong chương Aggregates (10). Chẳng hạn, phương thức `planBacklogItem()` của nó tạo ra một `BacklogItem` mới — vốn là một Aggregate sau đó được trả về cho client.

Để minh họa thiết kế của các Factory Method, hãy cùng xem xét ba phương thức trong Collaboration Context.

Bảng 11.1 Các vị trí đặt Factory Method trên Aggregate

| Bounded Context | Aggregate | Factory Method |
| --- | --- | --- |
| Identity and Access Context | Tenant | offerRegistrationInvitation() |
|  |  | provisionGroup() |
|  |  | provisionRole() |
|  |  | registerUser() |
| Collaboration Context | Calendar | scheduleCalendarEntry() |
|  | Forum | startDiscussion() |
|  | Discussion | post() |
| Agile PM Context | Product | planBacklogItem() |
|  |  | scheduleRelease() |
|  |  | scheduleSprint() |

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000436_9f07ce6fc76bfa8f080e993c3323b2b4437e5f9faed6a5c725b54c0a145cb0f7.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000437_abd9ecb1c83d77499a59d18f31b4ab7e74a1d5747f0f096b8e4a50b231dbaa1b.png)

## Creating CalendarEntry Instances

Hãy cùng nhìn vào thiết kế. Factory mà chúng ta đang xem xét hiện tại được đặt trực tiếp trên `Calendar` và được sử dụng để tạo ra các thể hiện `CalendarEntry`. Nhóm CollabOvation sẽ dẫn dắt chúng ta đi qua phần triển khai cụ thể.

Dưới đây là một bài kiểm thử được phát triển để chứng minh cách thức Factory Method của `Calendar` nên được sử dụng như thế nào:

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000438_9820ee3c01fceb15a1b13ffa79afe5d61c385954d66ba4029c37b798a66d5b84.png)

```java
public class CalendarTest extends DomainTest {
    private CalendarEntry calendarEntry;
    private CalendarEntryId calendarEntryId;
    ...
    public void testCreateCalendarEntry() throws Exception {
        Calendar calendar = this.calendarFixture();
        DomainRegistry.calendarRepository().add(calendar);
        DomainEventPublisher
            .instance()
            .subscribe(
                new DomainEventSubscriber<CalendarEntryScheduled>() {
                    public void handleEvent(CalendarEntryScheduled aDomainEvent) {
                        calendarEntryId = aDomainEvent.calendarEntryId();
                    }
                    public Class<CalendarEntryScheduled> subscribedToEventType() {
                        return CalendarEntryScheduled.class;
                    }
                });
        calendarEntry = calendar.scheduleCalendarEntry(
            DomainRegistry
                .calendarEntryRepository()
                .nextIdentity(),
```

## FACTORY METHOD ON AGGREGATE ROOT

```java
            new Owner("jdoe", "John Doe", "jdoe@lastnamedoe.org"),
            "Sprint Planning",
            "Plan sprint for first half of April 2012.",
            this.tomorrowOneHourTimeSpanFixture(),
            this.oneHourBeforeAlarmFixture(),
            this.weeklyRepetitionFixture(),
            "Team Room",
            new TreeSet<Invitee>(0));
        DomainRegistry.calendarEntryRepository().add(calendarEntry);
        assertNotNull(calendarEntryId);
        assertNotNull(calendarEntry);
        ...
    }
}
```

Có 9 tham số được truyền vào cho phương thức `scheduleCalendarEntry()`. Tuy nhiên, như bạn sẽ thấy ngay sau đây, constructor của `CalendarEntry` lại đòi hỏi tổng cộng tới 11 tham số. Chúng ta sẽ xem xét các lợi ích của việc này trong giây lát. Sau khi một `CalendarEntry` mới được tạo thành công, client bắt buộc phải thêm nó vào Repository của nó. Nếu không làm điều đó, thể hiện mới này sẽ bị bỏ trôi và bị dọn dẹp bởi bộ thu gom rác (garbage collector).

Phần assertion đầu tiên chứng minh rằng `CalendarEntryId` được publish cùng với Event phải khác null (`nonnull`), qua đó xác nhận rằng Event đã được publish thành công. Ở đây không phải là client trực tiếp của `Calendar` sẽ thực sự đăng ký lắng nghe Event đó, mà bài kiểm thử đang chứng minh rằng Event `CalendarEntryScheduled` trên thực tế đã được publish ra ngoài.

Thể hiện `CalendarEntry` mới cũng bắt buộc phải khác null (`nonnull`). Chúng ta có thể bổ sung thêm các assertion khác, nhưng hai assertion vừa trình bày là quan trọng nhất để làm tài liệu chứng minh cho thiết kế Factory Method và cách client sử dụng nó.

Bây giờ hãy xem phần hiện thực hóa của Factory Method:

```java
package com.saasovation.collaboration.domain.model.calendar;

public class Calendar extends Entity {
    ...
    public CalendarEntry scheduleCalendarEntry(
            CalendarEntryId aCalendarEntryId,
            Owner anOwner,
            String aSubject,
            String aDescription,
            TimeSpan aTimeSpan,
            Alarm anAlarm,
            Repetition aRepetition,
            String aLocation,
            Set<Invitee> anInvitees) {
```

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000439_289cf1689893e8b280c39213c336e1074a390c382ee888a45c25dda22c7dd456.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000440_9d0afe2c8825ef859421822ac7f089df170974514fdbdf3b87cc446897926d08.png)

## Chapter 11 FACTORIES

```java
        CalendarEntry calendarEntry = new CalendarEntry(
            this.tenant(),
            this.calendarId(),
            aCalendarEntryId,
            anOwner,
            aSubject,
            aDescription,
            aTimeSpan,
            anAlarm,
            aRepetition,
            aLocation,
            anInvitees);
        DomainEventPublisher
            .instance()
            .publish(new CalendarEntryScheduled(...));
        return calendarEntry;
    }
    ...
}
```