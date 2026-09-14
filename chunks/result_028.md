Khi phát triển các Aggregate (cụm thực thể / tập hợp đối tượng nhất quán trong DDD) với cơ chế persistence (lưu trữ dữ liệu bền vững) truyền thống (chẳng hạn như cơ sở dữ liệu quan hệ mà không sử dụng Event Sourcing - mô hình lưu trữ trạng thái dựa trên chuỗi sự kiện), sự trở ngại trong quá trình phát triển khi đưa một Entity (thực thể có định danh) mới vào hệ thống hoặc bổ sung dữ liệu cho một Entity sẵn có có thể thấy rất rõ ràng. Chúng ta cần phải tạo các bảng mới, định nghĩa các mapping schemata (lược đồ ánh xạ dữ liệu / ORM mapping) mới cùng các phương thức Repository (kho lưu trữ đối tượng nghiệp vụ) mới. Nếu xu hướng của chúng ta là ngại những chi phí phát sinh (overhead) phát triển như vậy, điều đó có thể khiến chúng ta làm phình to các Aggregate do dồn thêm nhiều cấu trúc trạng thái và hành vi vào từng Aggregate. Việc bổ sung thêm vào một Aggregate sẵn có thường dễ dàng hơn nhiều so với việc tạo ra một Aggregate mới.

Tuy nhiên, thiên kiến của chúng ta có thể thay đổi nếu các Aggregate được thiết kế mới một cách dễ dàng hơn, và tôi khẳng định điều này hoàn toàn đúng khi áp dụng Event Sourcing. Theo kinh nghiệm của tôi, các Aggregate được thiết kế bằng mô hình A+ES (Aggregates và Event Sourcing) thường có xu hướng nhỏ gọn hơn, và đây chính là một trong những Aggregate Rules of Thumb (nguyên tắc kinh nghiệm cốt lõi khi thiết kế Aggregate).

Chẳng hạn, đối với một công ty cung cấp phần mềm dạng dịch vụ (SaaS), một khách hàng ngoài đời thực có thể được biểu diễn bằng các Aggregate riêng biệt tập trung vào các khía cạnh hành vi khác nhau:

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000638_a41bb89d670873b41e7094443b58af01a462a7f6aceafff80e633cf861495dd8.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000639_b6320297582b352995194736747f8dd1708909cd65003b9c08ab66af47e0f1d8.png)

- Customer:505 đảm nhận các hành vi thanh toán, xuất hóa đơn và quản lý tài khoản chung.
- Security-Account:505 duy trì nhiều người dùng cùng các quyền truy cập tương ứng cho từng người.
- Consumer:505 theo dõi mức tiêu thụ dịch vụ thực tế.

Mỗi loại Aggregate này có thể được triển khai trong một Bounded Context (ngữ cảnh giới hạn) khác nhau, và mỗi Bounded Context lại sử dụng các công nghệ cùng phương pháp tiếp cận kiến trúc khác nhau. Ví dụ, khía cạnh Consumer có thể cần đáp ứng khả năng mở rộng quy mô cao và xử lý việc tiêu thụ hàng nghìn thông điệp cho khách hàng mỗi giây. Nếu đúng như vậy, một Event Stream (luồng sự kiện) như thế nên được lưu trữ và vận hành trên nền tảng đám mây tự động co giãn (autoscaling cloud fabric). Các khía cạnh khác có thể đòi hỏi ít tài nguyên hơn, cho phép chúng được triển khai trong một môi trường vận hành nhẹ nhàng hơn.

Dĩ nhiên, Aggregate không bao giờ nên bị thu nhỏ một cách tùy tiện. Chúng ta luôn muốn thiết kế Aggregate sao cho bảo vệ được các business invariants (bất biến / quy tắc toàn vẹn nghiệp vụ) thực sự, và việc làm này có thể khiến cho bất kỳ Aggregate nào cũng được cấu thành từ nhiều Entity cùng một số Value Objects (đối tượng giá trị). Dẫu vậy, sự tiện lợi khi sử dụng A+ES mang lại cho chúng ta cơ hội lớn hơn để hướng tới những thiết kế đơn giản và hiệu quả. Đây là một lợi thế cần được nắm bắt bất cứ khi nào có thể.

Trên thực tế, đôi khi việc bắt đầu mô hình hóa miền nghiệp vụ (domain modeling) bằng cách xác định phần cốt lõi của Ubiquitous Language (ngôn ngữ chung / ngôn ngữ toàn hiện) thông qua các Commands (lệnh thực thi) gửi đến và các Events (sự kiện) phát sinh ra, cũng như các hành vi được thực thi, lại rất hữu ích. Chỉ ở giai đoạn sau đó, chúng ta mới thực sự nhóm một số khái niệm lại thành Aggregate, dựa trên sự tương đồng, tính liên quan và các quy tắc nghiệp vụ. Cách tiếp cận này—ngay cả khi nó chỉ là một development spike (bước thử nghiệm kỹ thuật ngắn hạn) tạm thời dùng trong bài tập mô hình hóa miền nghiệp vụ—cũng có thể mang lại sự hiểu biết sâu sắc hơn về các khái niệm nghiệp vụ cốt lõi của chúng ta.

> 💡 **Giải thích thêm:** Trong phát triển phần mềm (đặc biệt là Extreme Programming và Agile), "spike" (hay "development spike") là một thử nghiệm kỹ thuật ngắn hạn nhằm mục đích nghiên cứu, trả lời một câu hỏi kỹ thuật cụ thể hoặc giảm thiểu rủi ro kiến trúc trước khi triển khai chính thức, không nhằm tạo ra mã nguồn hoàn chỉnh cho sản phẩm.  
> Nguồn tham khảo: [https://en.wikipedia.org/wiki/Spike_(software_development](https://en.wikipedia.org/wiki/Spike_(software_development))

## Read Model Projections

Một trong những mối bận tâm phổ biến đối với hướng thiết kế A+ES là làm thế nào để truy vấn các Aggregate dựa trên các thuộc tính của chúng. Event Sourcing không cung cấp một cách thức đơn giản nào để trả lời một câu hỏi như: "Tổng giá trị của tất cả các đơn hàng của khách hàng trong tháng vừa qua là bao nhiêu?" Trên thực tế, chúng ta sẽ cần phải tải lên bộ nhớ từng phiên bản (instance) Customer, duyệt qua tất cả các phiên bản Order trong tháng gần nhất của từng khách hàng, rồi tính tổng của chúng — điều này sẽ cực kỳ kém hiệu quả.

Đây chính là nơi Read Model Projections (các phép chiếu mô hình đọc dữ liệu) có thể hỗ trợ. Read Model Projections có thể được hiện thực hóa thông qua một tập hợp đơn giản các đối tượng đăng ký nhận Domain Event (sự kiện nghiệp vụ / sự kiện miền) được dùng để tạo và cập nhật một Read Model (mô hình phục vụ truy vấn dữ liệu) bền vững. Nói cách khác, chúng chiếu (project) các Event sang một Read Model bền vững. Khi các đối tượng đăng ký nhận Event tiếp nhận các Event mới, chúng sẽ tính toán các kết quả truy vấn và lưu trữ chúng vào Read Model để sử dụng sau này.

Tóm lại, một Projection rất tương đồng với một phiên bản Aggregate. Khi các Event được tiếp nhận và xử lý, chúng ta sử dụng dữ liệu từ chúng để xây dựng trạng thái của Projection. Read Model Projections được lưu trữ bền vững sau mỗi lần cập nhật và có thể được truy cập bởi nhiều bên đọc dữ liệu, cả bên trong lẫn bên ngoài Bounded Context.

## Projection Samples Are Available

Thông tin chi tiết hơn về việc sử dụng Projection, bao gồm mã nguồn cho các kịch bản lưu trữ dữ liệu khác nhau và cơ chế tự động xây dựng lại Read Model, hiện có sẵn trong dự án mẫu tại: [http://lokad.github.com/lokad-cqrs/](http://lokad.github.com/lokad-cqrs/).

Dưới đây là cách chúng ta có thể định nghĩa một Projection để ghi nhận toàn bộ các giao dịch cho từng Customer:

```csharp
public class CustomerTransactionsProjection {
    IDocumentWriter<CustomerId, CustomerTransactions> _store;

    public CustomerTransactionsProjection(IDocumentWriter<CustomerId, CustomerTransactions> store) {
        _store = store;
    }

    public void When(CustomerCreated e) {
        _store.Add(e.Id, new CustomerTransactions());
    }

    public void When(CustomerChargeAdded e) {
        _store.UpdateOrThrow(e.Id, v => v.AddTx(e.ChargeName, -e.Charge, e.NewBalance, e.TimeUtc));
    }

    public void When(CustomerPaymentAdded e) {
        _store.UpdateOrThrow(e.Id, v => v.AddTx(e.PaymentName, e.Payment, e.NewBalance, e.TimeUtc));
    }
}
```

Lớp Projection này tương tự như một Application Service (dịch vụ ứng dụng) được thiết kế cho A+ES có sử dụng biểu thức lambda. Tuy nhiên, Projection của chúng ta phản ứng với Event thay vì Command và cập nhật tài liệu (document) thông qua IDocumentWriter, thay vì cập nhật các phiên bản Aggregate.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000640_1365b7b0b7075d536b21fc8ab77670e944da48b03dc9e9d93a0386e6f332d4e3.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000641_9d297339e70d73a9d68337522d9fd199b005ddb002fffc236404ab24613d03d7.png)

Read Model bên dưới thực chất chỉ là một Data Transfer Object (DTO - đối tượng truyền dữ liệu) [Fowler] đơn giản, có thể được tuần tự hóa (serialized) và lưu trữ bền vững vào một kho lưu trữ nền tảng nào đó bằng IDocumentWriter:

```csharp
[Serializable]
public class CustomerTransactions {
    public IList<CustomerTransaction> Transactions = new List<CustomerTransaction>();

    public void AddTx(
        string name,
        CurrencyAmount change,
        CurrencyAmount balance,
        DateTime timeUtc) {
        Transactions.Add(new CustomerTransaction() {
            Name = name,
            Balance = balance,
            Change = change,
            TimeUtc = timeUtc
        });
    }
}

[Serializable]
public class CustomerTransaction {
    public CurrencyAmount Change;
    public CurrencyAmount Balance;
    public string Name;
    public DateTime TimeUtc;
}
```

Việc lưu trữ các Read Model trong cơ sở dữ liệu dạng tài liệu (document database) là một thực hành phổ biến, mặc dù vẫn có thể áp dụng các phương án khác. Chúng ta có thể lưu tạm (cache) Read Model trong bộ nhớ (ví dụ: một phiên bản memcached), đẩy chúng dưới dạng tài liệu vào mạng phân phối nội dung (CDN - Content Delivery Network), hoặc lưu trữ chúng trong các bảng cơ sở dữ liệu quan hệ.

Bên cạnh khả năng mở rộng quy mô, một trong những ưu điểm vượt trội của Projection là chúng hoàn toàn có thể loại bỏ và tạo lại (disposable). Chúng có thể được thêm mới, sửa đổi hoặc thay thế toàn bộ vào bất kỳ thời điểm nào trong vòng đời của ứng dụng. Để thay thế toàn bộ Read Model, hãy hủy bỏ mọi dữ liệu Read Model hiện có và tạo dữ liệu mới bằng cách cho toàn bộ Event Stream chạy qua các lớp Projection của bạn. Quy trình này có thể được tự động hóa. Thậm chí chúng ta còn có thể ngăn chặn hoàn toàn thời gian chết (zero downtime) trong khi thực hiện thay thế toàn bộ Read Model.

## Use with Aggregate Design

Các Read Model Projection như vậy thường được dùng để hiển thị thông tin cho các client khác nhau (chẳng hạn như giao diện người dùng trên web và ứng dụng máy tính để bàn), nhưng chúng cũng rất hữu ích để chia sẻ thông tin giữa các Bounded Context và các Aggregate của chúng. Hãy xem xét kịch bản trong đó một Aggregate Invoice cần một số thông tin của Customer (ví dụ: tên, địa chỉ thanh toán và mã số thuế) để tính toán và chuẩn bị một Invoice hợp lệ. Chúng ta có thể thu thập thông tin này dưới dạng dễ sử dụng thông qua CustomerBillingProjection, lớp này sẽ tạo và duy trì một phiên bản độc quyền của CustomerBillingView. Read Model này được cung cấp cho Aggregate Invoice thông qua một Domain Service (dịch vụ nghiệp vụ) có tên là IProvideCustomerBillingInformation. Đằng sau hậu trường, Domain Service này chỉ việc truy vấn kho lưu trữ tài liệu để lấy phiên bản CustomerBillingView tương ứng.

Projection cũng giúp chúng ta chia sẻ thông tin giữa các phiên bản Aggregate theo cách giảm thiểu liên kết phụ thuộc (loosely coupled) và dễ bảo trì hơn. Nếu tại bất kỳ thời điểm nào chúng ta cần thay đổi thông tin do IProvideCustomerBillingView trả về, chúng ta có thể thực hiện mà không cần chỉnh sửa Aggregate Customer. Chúng ta chỉ cần thay đổi phần triển khai của Projection và xây dựng lại các Read Model bằng cách phát lại (replay) toàn bộ các Event.

## Events Enrichment

Một trong những vấn đề phổ biến hơn với các thiết kế A+ES bắt nguồn từ mục đích kép của chúng. Các Event vừa được sử dụng cho việc lưu trữ Aggregate bền vững, vừa được dùng để truyền đạt các diễn biến ở cấp độ nghiệp vụ trong toàn bộ doanh nghiệp thông qua cơ chế phát tán sự kiện (Event publishing).

Ví dụ, hãy xem xét trường hợp sau: Một hệ thống quản lý dự án cho phép khách hàng tạo dự án mới và lưu trữ (archive) các dự án đã hoàn thành. Hãy hình dung chúng ta phát tán một Event ProjectArchived mỗi khi người dùng lưu trữ một dự án. Domain Event này có thể có thiết kế như sau:

```csharp
public class ProjectArchived {
    public ProjectId Id { get; set; }
    public UserId ChangeAuthorId { get; set; }
    public DateTime ArchivedUtc { get; set; }
    public string OptionalComment { get; set; }
}
```

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000642_c63b6b969620845ba2a97b13bd32a36897d78098d3c481e1a568e479d49d9cc7.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000643_03e0a97de841a4bb5d486a436efb1038a7b4defa594b887563ecb6e72d97070b.png)

Figure A.16 Nhiều Domain Event được một Projection tiếp nhận và sử dụng để xây dựng một khung nhìn (view) của Read Model.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000644_f28b2fa883eb0f361467c8b6308f1abee66713dafaa27d807da92c1908d07ed6.png)

Thông tin này đủ phong phú để tái tạo một Project đã lưu trữ bằng A+ES. Tuy nhiên, nếu được thiết kế theo cách này, Event của chúng ta có thể gây ra nhiều trở ngại cho các bên tiêu thụ.

Tại sao lại như vậy? Hãy xem xét Projection cho khung nhìn ArchivedProjectsPerCustomer, như minh họa trong Hình A.16. Nó đăng ký nhận các Event và duy trì một danh sách các dự án đã lưu trữ theo từng khách hàng. Để hoàn thành nhiệm vụ, Projection này sẽ cần thông tin mới nhất về những dữ liệu như:

* Tên dự án
* Tên khách hàng
* Việc phân công dự án cho khách hàng
* Các Event lưu trữ dự án

Chúng ta có thể đơn giản hóa Projection này đáng kể bằng cách làm giàu (enrich) Event ProjectArchived với các trường dữ liệu bổ sung để gửi kèm những thông tin liên quan. Các trường dữ liệu bổ sung này không bắt buộc đối với việc tái tạo trạng thái của Aggregate tương ứng, nhưng sẽ giúp đơn giản hóa rõ rệt cho các đối tượng tiêu thụ Event của chúng ta. Hãy xem xét bản hợp đồng (contract) Event thay thế sau:

```csharp
public class ProjectArchived {
    public ProjectId Id { get; set; }
    public string ProjectName { get; set; }
    public UserId ChangeAuthorId { get; set; }
    public DateTime ArchivedUtc { get; set; }
```

```csharp
    public string OptionalComment { get; set; }
    public CustomerId Customer { get; set; }
    public string CustomerName { get; set; }
}
```

Nhờ Event mới được bổ sung dữ liệu này, ArchivedProjectsPerCustomerView do Projection tạo ra có thể được đơn giản hóa như thể hiện trong Hình A.17.

Một nguyên tắc kinh nghiệm về Domain Event là hãy thiết kế chúng với lượng thông tin đủ để đáp ứng 80% các đối tượng đăng ký (subscribers), cho dù việc này đòi hỏi các Event phải mang nhiều thông tin hơn mức cần thiết đối với một lượng lớn đối tượng đăng ký. Hãy luôn nhớ rằng chúng ta muốn đảm bảo các bộ xử lý Projection khung nhìn có được một tập dữ liệu Event phong phú, chúng ta thường đưa vào:

* Các định danh Entity, vốn là các chủ thể/chủ sở hữu của Event, chẳng hạn như CustomerId đối với Customer
* Tên gọi và các thuộc tính khác thường được dùng cho mục đích hiển thị, chẳng hạn như ProjectName, CustomerName và những thông tin tương tự

Đây là các khuyến nghị, không phải quy tắc cứng nhắc. Chúng thường phát huy hiệu quả tốt cho các doanh nghiệp có nhiều Bounded Context khác nhau. Các Bounded Context nguyên khối (monolithic) nhận được ít lợi ích hơn từ các gợi ý này, vì chúng thường có xu hướng duy trì các bảng tra cứu phụ và các ánh xạ Entity. Dĩ nhiên, bạn là người hiểu rõ nhất những thuộc tính nào nên được đưa vào các Event của mình. Đôi khi, việc xác định những thuộc tính nào thuộc về một loại Event nhất định là hết sức hiển nhiên, và với những trường hợp đó, chúng ta hiếm khi cần phải tái cấu trúc (refactoring).

Figure A.17 Các Domain Event như ProjectArchived có thể được tiếp nhận bởi các bộ xử lý Projection để sinh ra các Read Model phục vụ riêng cho khung nhìn và báo cáo.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000645_f2245c46135b90b225e08955b9b0a6da45060c5377fadcb04457e30b8e88fa41.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000646_9ba04f28f3cf9811ffee6c4158814dbed75c341b70814fcaa986a649629b2aec.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000647_618c7536faf3e224885cdabb1ddccf1e99c00b39a727c16ad3fc51887a333e47.png)

## Supporting Tools and Patterns

Việc phát triển, xây dựng, triển khai và bảo trì các hệ thống sử dụng A+ES đòi hỏi một tập hợp các mẫu (patterns) có phần khác biệt so với các hệ thống truyền thống. Phần này trình bày một số mẫu, công cụ và thực hành đã được chứng minh là rất hữu ích khi áp dụng A+ES.

## Event Serializers

Việc lựa chọn một bộ tuần tự hóa (serializer) hỗ trợ tốt cho việc quản lý phiên bản (versioning) và đổi tên Event là một quyết định khôn ngoan. Điều này đặc biệt đúng ở giai đoạn đầu của một dự án A+ES, khi mô hình miền nghiệp vụ có xu hướng tiến hóa rất nhanh. Hãy xem xét Event sau, được khai báo bằng cách sử dụng các chú thích (annotations) của một bản triển khai Protocol Buffers 1 trên .NET:

```csharp
[DataContract]
public class ProjectClosed {
    [DataMember(Order = 1)]
    public long ProjectId { get; set; }

    [DataMember(Order = 2)]
    public DateTime Closed { get; set; }
}
```

Bây giờ, nếu chúng ta tuần tự hóa ProjectClosed bằng DataContractSerializer hoặc JsonSerializer thay vì Protocol Buffers, bất kỳ thành viên nào bị đổi tên đều có thể dễ dàng làm gián đoạn hoặc hỏng (break) các bên tiêu thụ phụ thuộc. Ví dụ, giả sử bạn đổi tên thuộc tính Closed thành ClosedUtc. Trừ khi bạn đặc biệt chú ý ánh xạ thuộc tính đã đổi tên này trong Bounded Context tiêu thụ, nếu không bạn sẽ gây ra một lỗi rất khó hiểu hoặc sinh ra dữ liệu sai lệch:

```csharp
[DataContract]
public class ProjectClosed {
    [DataMember]
    public long ProjectId { get; set; }

    [DataMember(Name = "Closed")]
    public DateTime ClosedUtc { get; set; }
}
```

Protocol Buffers đáp ứng tốt các tình huống tuần tự hóa liên tục biến đổi vì nó theo dõi các thành viên trong hợp đồng bằng các thẻ số nguyên (integral tags), chứ không phải bằng tên gọi. Như có thể thấy trong đoạn mã sau, các client có thể sử dụng thành công Close hoặc CloseUtc làm tên thuộc tính. Nó tuần tự hóa các đối tượng cực kỳ nhanh và tạo ra biểu diễn nhị phân rất nhỏ gọn. Nhờ sử dụng Protocol Buffers, chúng ta có thể đổi tên các thuộc tính của Event mà không phải lo lắng về tính tương thích ngược (backward compatibility), từ đó giảm thiểu trở ngại phát triển trong một mô hình miền đang trên đà tiến hóa.

1. Protocol Buffers có nguồn gốc từ Google. Các bên khác đã tạo ra các bản triển khai trên .NET.

```csharp
[DataContract]
public class ProjectClosed {
    [DataMember(Order = 1)]
    public long ProjectId { get; set; }

    [DataMember(Order = 2)]
    public DateTime ClosedUtc { get; set; }
}
```

Một số công cụ tuần tự hóa đa nền tảng bổ sung bao gồm Apache Thrift, Avro và MessagePack, mang đến nhiều sự lựa chọn rất đáng cân nhắc.

## Event Immutability

Về bản chất, các Event Stream vốn được coi là bất biến (immutable). Để giữ cho mô hình phát triển nhất quán với khái niệm này (đồng thời tránh các tác dụng phụ không mong muốn), các hợp đồng Event cần được triển khai dưới dạng bất biến. Để làm được điều đó với C# trên .NET, chúng ta đánh dấu các trường là chỉ đọc (read-only) và chỉ thiết lập giá trị thông qua hàm khởi tạo (constructor). Dựa trên Event ProjectClosed trước đó, chúng ta có thể tạo một bản triển khai bất biến như sau:

```csharp
[DataContract]
public class ProjectClosed {
    [DataMember(Order = 1)]
    public long ProjectId { get; private set; }

    [DataMember(Order = 2)]
    public DateTime ClosedUtc { get; private set; }

    public ProjectClosed(long projectId, DateTime closedUtc) {
        ProjectId = projectId;
        ClosedUtc = closedUtc;
    }
}
```

## Value Objects

Như đã được thảo luận kỹ lưỡng trong Value Objects (6), đây là một mẫu có thể đơn giản hóa đáng kể quá trình phát triển và tiến hóa của các mô hình miền phong phú. Khi sử dụng Value Object, chúng ta kết hợp các kiểu nguyên thủy (primitive types) có tính gắn kết cao thành một kiểu dữ liệu bất biến được đặt tên tường minh. Chẳng hạn, thay vì khai báo định danh của một dự án dưới dạng kiểu `long`, chúng ta sẽ mô hình hóa một `ProjectId` tường minh:

```csharp
public struct ProjectId {
    public ProjectId(long id) {
        Id = id;
    }
```

```csharp
    public readonly long Id { get; private set; }
}
```

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000648_2dc72a73392d2bb3f0c0e4c2c9d42d84fc449f347519991f0c3a999596146b57.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000649_c78ba36c119882e952f2b99172c8a80bfb668bd06f38ecdc9ea8b12c800ae2ad.png)

```csharp
    public override string ToString() {
        return string.Format("Project-{0}", Id);
    }
}
```

Chúng ta vẫn sử dụng kiểu `long` để chứa giá trị số định danh thực tế, nhưng dùng kiểu `ProjectId` để phân biệt nó với tất cả các kiểu dữ liệu khác. Kiểu giá trị dĩ nhiên không chỉ giới hạn ở các định danh duy nhất. Những kiểu giá trị phù hợp khác có thể kể đến như các đối tượng tiền tệ (đặc biệt trong các hệ thống đa tiền tệ), địa chỉ, email, các đơn vị đo lường, v.v.

Ngoài việc làm giàu thông tin và tăng tính biểu đạt cho các hợp đồng Event và Command, các Value Object trong miền còn mang lại nhiều lợi ích thực tế hơn cho các bản triển khai A+ES, chẳng hạn như khả năng kiểm tra kiểu tĩnh (static type checking) và sự hỗ trợ từ IDE. Hãy xem xét tình huống sau, nơi một lập trình viên có thể vô tình đặt nhầm các tham số của một hàm khởi tạo Event đơn giản bằng cách truyền sai thứ tự của chúng:

```csharp
long customerId = ...;
long projectId = ...;
var event = new ProjectAssignedToCustomer(customerId, projectId);
```

Đây là một lỗi mà trình biên dịch sẽ không thể phát hiện ra, và có thể chỉ được tìm thấy sau rất nhiều công sức gỡ lỗi (debug) cùng sự ức chế. Tuy nhiên, nếu bạn sử dụng các Value Object làm định danh, trình biên dịch (và do đó là trình soạn thảo IDE) sẽ bắt được lỗi khi truyền CustomerId trước và ProjectId sau:

```csharp
CustomerId customerId = ...;
ProjectId projectId = ...;
var event = new ProjectAssignedToCustomer(customerId, projectId);
```

Các lợi ích thậm chí còn trở nên rõ ràng hơn khi bạn có các lớp hợp đồng dạng phẳng (flat) chứa một lượng lớn các trường dữ liệu. Chẳng hạn, hãy xem xét Event sau (đã được đơn giản hóa từ phiên bản thực tế trên môi trường production):

```csharp
public class CustomerInvoiceWritten {
    public InvoiceId Id { get; private set; }
    public DateTime CreatedUtc { get; private set; }
    public CurrencyType Currency { get; private set; }
    public InvoiceLine[] Lines { get; private set; }
    public decimal SubTotal { get; private set; }
    public CustomerId Customer { get; private set; }
    public string CustomerName { get; private set; }
    public string CustomerBillingAddress { get; private set; }
```

```csharp
    public float OptionalVatRatio { get; private set; }
    public string OptionalVatName { get; private set; }
    public decimal VatTax { get; private set; }
    public decimal Total { get; private set; }
}
```

Như bạn có thể hình dung, việc làm việc với một lớp có quá nhiều thuộc tính 2 có thể khá phức tạp. Chúng ta có thể tái cấu trúc Event cồng kềnh này để trở nên tường minh và dễ đọc hơn bằng cách tinh chỉnh mô hình của nó theo các khái niệm nghiệp vụ sẵn có:

```csharp
public class CustomerInvoiceWritten {
    public InvoiceId Id { get; private set; }
    public InvoiceHeader Header { get; private set; }
    public InvoiceLine[] Lines { get; private set; }
    public InvoiceFooter Footer { get; private set; }
}
```

InvoiceHeader và InvoiceFooter cấu thành các nhóm thuộc tính có tính gắn kết cao:

```csharp
public class InvoiceHeader {
    public DateTime CreatedUtc { get; private set; }
    public CustomerId Customer { get; private set; }
    public string CustomerName { get; private set; }
    public string CustomerBillingAddress { get; private set; }
}

public class InvoiceFooter {
    public CurrencyAmount SubTotal { get; private set; }
    public VatInformation OptionalVat { get; private set; }
    public CurrencyAmount VarAmount { get; private set; }
    public CurrencyAmount Total { get; private set; }
}
```

Chúng ta đã thay thế các thuộc tính riêng rẽ là `CurrencyType Currency` và `decimal SubTotal` bằng một Value Object `CurrencyAmount`. Một lợi ích bổ sung là lớp này có thể được tăng cường thêm logic kiểm tra tính hợp lệ (sanity check) nhằm ngăn chặn các phép tính toán giữa các số tiền khác đơn vị tiền tệ cũng như những thao tác không hợp lệ khác. Tương tự, thông tin thuế VAT cũng được gộp vào một Value Object riêng biệt rồi được ghép vào `InvoiceFooter` cùng với các tổng tiền khác của hóa đơn.

Bất cứ khi nào có thể, chúng ta nên nỗ lực áp dụng các Value Object, cho dù là đối với các đối tượng Command, Event hay các thành phần của Aggregate.

2. Dữ liệu thực nghiệm chứng minh một nguyên tắc kinh nghiệm phù hợp: Mỗi lớp không nên có quá từ 5 đến 7 thuộc tính thành viên.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000650_2f247caa7445b1814eff353ed0b64437149eee46d8daa44392a7c8bbba7f6bba.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000651_860ac12ddc9695003b832d9341d99019bccb992ebb9f945b6495b5cef6a5e6d4.png)

Rõ ràng, việc sử dụng Value Object trong Command và/hoặc Event sẽ đòi hỏi phải triển khai (deploy) chúng cùng nhau, hoặc thậm chí là tạo ra một Shared Kernel (hạt nhân chia sẻ) (3). Tuy nhiên, một số miền nghiệp vụ cực kỳ phức tạp có thể yêu cầu thiết kế các Value Object chứa logic nghiệp vụ hết sức rối rắm. Trong những trường hợp như vậy, việc đưa các Value Object đó vào một Shared Kernel chỉ nhằm mục đích giải tuần tự hóa an toàn kiểu (type-safe deserialization) rất có thể sẽ dẫn đến một thiết kế mỏng manh, dễ gãy (brittle). Việc phân biệt giữa các lớp chia sẻ đơn giản dùng để giải tuần tự hóa dữ liệu Command và Event theo cách an toàn kiểu với các lớp phức tạp hơn do Core Domain (miền nghiệp vụ cốt lõi) (2) đòi hỏi có thể sẽ mang lại hiệu quả. Điều đó đồng nghĩa với việc tạo ra hai bộ lớp Value Object: một bộ dành riêng cho Core Domain và một bộ được triển khai cùng các lớp Command và Event. Dữ liệu do hai bộ này nắm giữ sẽ được chuyển đổi qua lại khi cần thiết.

Tùy vào quan điểm của bạn, việc nhân bản các lớp có thể có vẻ phức tạp hơn mức cần thiết, dẫn bạn đến con đường tạo ra sự phức tạp ngẫu nhiên (accidental complexity) trong hệ thống. Nếu bạn có quan điểm đó, có thể nên cân nhắc một phương pháp tiếp cận khác. Một giải pháp thay thế là chuẩn hóa các Event đã tuần tự hóa thành một Published Language (ngôn ngữ công bố chung) (3). Như đã giải thích trong Integrating Bounded Contexts (13), bạn có thể chọn tiêu thụ các thông báo Event bằng cách tiếp cận định kiểu động (dynamic typing). Cách làm này sẽ loại bỏ sự cần thiết của việc phải triển khai các kiểu Event và Value Object đến các bên đăng ký tiêu thụ. Tương tự như mọi phương pháp tiếp cận khác, giải pháp này cũng có những đánh đổi (trade-offs) cần phải cân nhắc kỹ lưỡng.

## Contract Generation

Việc duy trì hàng trăm hợp đồng Event (và Command) bằng phương pháp thủ công vừa tẻ nhạt lại vừa dễ phát sinh lỗi. Sẽ hiệu quả hơn nhiều nếu diễn đạt các định nghĩa của chúng bằng một Domain-Specific Language (DSL - ngôn ngữ đặc thù miền) cô đọng, có thể dùng để sinh mã nguồn đơn giản bằng cách tạo ra các lớp chuẩn xác ngay tại thời điểm biên dịch (build time). Có một vài cách để định hình cú pháp DSL, và chúng ta có thể cân nhắc định dạng `.proto` của Protocol Buffer hoặc một định dạng tương tự làm hướng đi. Chẳng hạn, bạn có thể thấy cách tiếp cận sau đây rất hữu ích:

CustomerInvoiceWritten!(InvoiceId Id, InvoiceHeader header, InvoiceLine[] lines, InvoiceFooter footer)

Một bộ sinh mã đơn giản có thể sử dụng cú pháp DSL đã được phân tích cú pháp (parsed) để sinh mã cho từng dòng nguồn. Hãy chú ý một ví dụ ở đây, trong đó CustomerInvoiceWritten được sinh ra từ DSL nêu trên:

```csharp
[DataContract]
public sealed class CustomerInvoiceWritten : IDomainEvent {
    [DataMember(Order = 1)]
    public InvoiceId Id { get; private set; }

    [DataMember(Order = 2)]
    public InvoiceHeader Header { get; private set; }

    [DataMember(Order = 3)]
    public InvoiceLine[] Lines { get; private set; }

    [DataMember(Order = 4)]
    public InvoiceFooter Footer { get; private set; }

    public CustomerInvoiceWriter(
        InvoiceId id,
        InvoiceHeader header,
        InvoiceLine[] lines,
        InvoiceFooter footer) {
        Id = id;
        Header = header;
        Lines = lines;
        Footer = footer;
    }

    // bắt buộc bởi serializer
    ProjectClosed() {
        Lines = new InvoiceLine[0];
    }
}
```

Điều này mang lại những lợi ích thực tế sau:

* Nó giảm thiểu trở ngại trong quá trình phát triển bằng cách tạo điều kiện cho các vòng lặp mô hình hóa miền diễn ra nhanh hơn.
* Nó giảm thiểu xác suất lỗi do con người thường gặp khi làm việc thủ công.
* Cách biểu diễn cô đọng cho phép chúng ta theo dõi toàn bộ định nghĩa Event trên một màn hình duy nhất, cung cấp một bức tranh toàn cảnh để hiểu sâu sắc hơn. Điều này thậm chí có thể đóng vai trò như một bảng thuật ngữ ngắn gọn cho Ubiquitous Language.
* Chúng ta có thể quản lý phiên bản và phân phối các hợp đồng Event dưới dạng các định nghĩa cô đọng thay vì đòi hỏi mã nguồn hoặc mã nhị phân (binary code). Điều này thậm chí có thể giúp nâng cao khả năng cộng tác giữa các đội ngũ khác nhau.

Cách làm tương tự cũng có thể áp dụng cho các hợp đồng Command. Bản triển khai mã nguồn mở của công cụ sinh mã dựa trên DSL cùng với các ví dụ hiện có sẵn trong dự án mẫu.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000652_849b8fdc64dccce41ad7d043d22b7d8c5dcf275918a11d6f14a455ce783ba55c.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000653_4234db078317150de0b9c580c0f9d7335f9c06de96bd78c46a68c1232611740f.png)

## Unit Testing and Specifications

Hãy xem xét một lợi ích bổ sung của việc sử dụng Event Sourcing khi chúng ta tạo các bài kiểm thử đơn vị (unit tests). Chúng ta có thể dễ dàng đặc tả các bài kiểm thử của mình dưới dạng Given-When-Expect (Giả định - Khi - Kỳ vọng), như sau:

1. Given các Event trong quá khứ
2. When phương thức của Aggregate được gọi
3. Expect các Event sau đây hoặc một ngoại lệ (exception)

Cách thức hoạt động như sau: Các Event trong quá khứ được sử dụng để thiết lập trạng thái của một Aggregate tại thời điểm bắt đầu bài kiểm thử đơn vị. Sau đó, chúng ta thực thi phương thức Aggregate đang được kiểm thử, cung cấp các đối số kiểm thử và các bản triển khai giả lập (mock implementations) của các Domain Service khi cần thiết. Cuối cùng, chúng ta khẳng định (assert) các kết quả kỳ vọng bằng cách so sánh các Event do Aggregate tạo ra với các Event kỳ vọng.

Cách tiếp cận này cho phép chúng ta nắm bắt và kiểm chứng các hành vi gắn liền với từng Aggregate. Đồng thời, chúng ta vẫn hoàn toàn không bị ràng buộc (decoupled) với cấu trúc trạng thái bên trong của Aggregate. Điều này giúp giảm tính mong manh dễ hỏng của bài kiểm thử (test fragility), vì các đội ngũ phát triển có thể thay đổi và tối ưu hóa bản triển khai của từng Aggregate theo bất kỳ cách nào, miễn là các hợp đồng hành vi vẫn được thỏa mãn như đã được xác nhận bởi các bài kiểm thử đơn vị.

Hoàn toàn có thể tiến thêm một bước nữa với cách tiếp cận này bằng cách biểu đạt mệnh đề When trực tiếp thông qua một Command, lệnh này sau đó được chuyển đến Application Service phù hợp đang chứa Aggregate được kiểm thử. Điều này cho phép chúng ta diễn đạt bài kiểm thử đơn vị như một bản đặc tả được thể hiện hoàn toàn bằng các thuật ngữ của Ubiquitous Language, thông qua mã nguồn hoặc bằng cách tạo ra một DSL.

Chỉ với một chút mã lệnh, các bản đặc tả như vậy có thể được tự động in ra dưới dạng các use case (trường hợp sử dụng) dễ đọc mà các chuyên gia nghiệp vụ (domain experts) có thể hiểu được. Những định nghĩa use case này có thể giúp các đội ngũ dự án giao tiếp tốt hơn xoay quanh các miền nghiệp vụ có hành vi phức tạp, từ đó nâng cao hiệu quả mô hình hóa của họ.

Dưới đây là một bản đặc tả đơn giản được định nghĩa bởi một tài liệu văn bản:

```text
[Passed] Use case 'Add Customer Payment - Unlock On Payment'.
```

```text
Given:
  1. Created customer 7 Eur 'Northwind' with key c67b30 ...
  2. Customer locked
When:
  Add 'unlock' payment 10 EUR via unlock
Expectations:
  [ok] Tx 1: payment 10 EUR 'unlock' (none)
  [ok] Customer unlocked
```

Nếu bạn quan tâm đến cách tiếp cận này, việc tìm kiếm trên web với từ khóa 'Event Sourcing Specifications' sẽ mang lại những hướng dẫn chi tiết.

## Event Sourcing in Functional Languages

Các mẫu triển khai được phác thảo trước đó tập trung vào phương pháp hướng đối tượng, vốn rất phù hợp cho các ngôn ngữ lập trình như Java và C#. Tuy nhiên, bản chất của Event Sourcing vốn dĩ mang tính hàm (functional). Vì vậy, nó có thể được triển khai rất thành công với các ngôn ngữ lập trình hàm như F# và Clojure. Làm như vậy có khả năng mang lại mã nguồn cô đọng hơn và đạt hiệu năng tối ưu.

Dưới đây là một số đặc thù khi chuyển từ phương pháp tiếp cận hướng đối tượng sang hướng hàm đối với các bản triển khai Aggregate:

* Chúng ta phải chuyển từ việc dùng một đối tượng trạng thái Aggregate có thể biến đổi (mutable) trong hướng đối tượng sang việc thiết kế một bản ghi trạng thái bất biến (immutable state record) đơn giản cùng một tập hợp các hàm biến đổi. Các hàm biến đổi này chỉ đơn giản nhận vào một bản ghi trạng thái và các đối số Event, rồi trả về một bản ghi trạng thái mới dưới dạng kết quả. Điều này rất giống với thiết kế của một Value Object bất biến, nơi mà các Side-Effect-Free Functions (hàm không gây tác dụng phụ) chỉ tạo ra các Giá trị mới dựa trên trạng thái của chính nó và các đối số của hàm. Những hàm như vậy có dạng `Func<State, Event, State>`.
* Trạng thái hiện tại của Aggregate có thể được định nghĩa như một phép left fold (phép gập trái / tích lũy từ trái sang phải) của tất cả các Event trong quá khứ được truyền vào các hàm biến đổi.
* Các phương thức Aggregate cũng có thể được biến đổi thành một tập hợp các hàm không lưu trạng thái (stateless functions), nhận vào các tham số Command, Domain Services và một trạng thái. Các hàm như vậy trả về không hoặc nhiều Event và có dạng `Func<TArg1, Event[] State, TArg2...,>`.
* Một Event Store có thể được nhìn nhận và diễn đạt như một cơ sở dữ liệu hàm (functional database), bởi vì nó lưu trữ bền vững các đối số truyền vào các hàm có nhiệm vụ làm biến đổi trạng thái của Aggregate. Việc hỗ trợ snapshot (ảnh chụp trạng thái nhanh) trong một Event Store dạng hàm là khái niệm quen thuộc đối với các lập trình viên hàm dưới tên gọi memoization (kỹ thuật ghi nhớ kết quả tính toán).

> 💡 **Giải thích thêm:** "Left fold" (hay `foldl`/`reduce`) trong lập trình hàm là phép toán duyệt tuần tự một danh sách từ trái qua phải, áp dụng một hàm tích lũy lên giá trị tích lũy hiện tại và từng phần tử để sinh ra giá trị kết quả duy nhất. Trong ngữ cảnh Event Sourcing, toàn bộ lịch sử các sự kiện trong quá khứ chính là một danh sách: bắt đầu từ trạng thái khởi tạo rỗng (`initial state`), mỗi sự kiện được áp dụng tuần tự qua hàm biến đổi để "tích lũy" và tái tạo chính xác trạng thái hiện tại của Aggregate.
> Nguồn tham khảo: [https://en.wikipedia.org/wiki/Fold_(higher-order_function](https://en.wikipedia.org/wiki/Fold_(higher-order_function))

Một development spike nhằm nắm bắt các khái niệm nghiệp vụ cốt lõi bằng A+ES trong một ngôn ngữ lập trình hàm có thể thúc đẩy nhanh chóng những nỗ lực mô hình hóa miền của chúng ta. Hơn thế nữa, nó buộc chúng ta phải chuyển trọng tâm khám phá miền từ cấu trúc của Aggregate sang việc phản ánh chặt chẽ Ubiquitous Language của miền được thể hiện thông qua các hành vi của nó. Bất kỳ điều gì có thể giúp chúng ta chú trọng nhiều hơn vào Core Domain và ít phụ thuộc hơn vào công nghệ đều có khả năng mang lại nhiều giá trị hơn cho doanh nghiệp và giúp doanh nghiệp đạt được lợi thế cạnh tranh lớn hơn nữa.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000654_a4c499d1fb3c0225991851444f0350d6ec11ff1645c2b28f22386b5313ec52d9.png)

This page intentionally left blank

## Bibliography

[Appleton, LoD] Appleton, Brad. n.d. 'Introducing Demeter and Its Laws.' [www.bradapp.com/docs/demeter-intro.html](https://www.bradapp.com/docs/demeter-intro.html).

[Bentley] Bentley, Jon. 2000. Programming Pearls, Second Edition. Boston, MA: Addison-Wesley.

[http://cs.bell-labs.com/cm/cs/pearls/bote.html](http://cs.bell-labs.com/cm/cs/pearls/bote.html).

[Brandolini] Brandolini, Alberto. 2009. 'Strategic Domain-Driven Design with Context Mapping.'

[www.infoq.com/articles/ddd-contextmapping](https://www.infoq.com/articles/ddd-contextmapping).

[Buschmann et al.] Buschmann, Frank, et al. 1996. Pattern-Oriented Software Architecture, Volume 1: A System of Patterns . New York: Wiley.

[Cockburn] Cockburn, Alastair. 2012. 'Hexagonal Architecture.'

[http://alistair.cockburn.us/Hexagonal+architecture](http://alistair.cockburn.us/Hexagonal+architecture).

[Crupi et al.] Crupi, John, et al. n.d. 'Core J2EE Patterns.'

[http://corej2eepatterns.com/Patterns2ndEd/DataAccessObject.htm](http://corej2eepatterns.com/Patterns2ndEd/DataAccessObject.htm).

[Cunningham, Checks] Cunningham, Ward. 1994. 'The CHECKS Pattern Language of Information Integrity.'

[http://c2.com/ppr/checks.html](http://c2.com/ppr/checks.html).

[Cunningham, Whole Value] Cunningham, Ward. 1994. '1. Whole Value.' [http://c2.com/ppr/checks.html#1](http://c2.com/ppr/checks.html#1).

[Cunningham, Whole Value aka Value Object] Cunningham, Ward. 2005. 'Whole Value.'

[http://fit.c2.com/wiki.cgi?WholeValue](http://fit.c2.com/wiki.cgi?WholeValue).

[Dahan, CQRS] Dahan, Udi. 2009. 'Clarified CQRS.'

[www.udidahan.com/2009/12/09/clarified-cqrs/](https://www.udidahan.com/2009/12/09/clarified-cqrs/).

[Dahan, Roles] Dahan, Udi. 2009. 'Making Roles Explicit.' [www.infoq.com/presentations/Making-Roles-Explicit-Udi-Dahan](https://www.infoq.com/presentations/Making-Roles-Explicit-Udi-Dahan).

[Deutsch] Deutsch, Peter. 2012. 'Fallacies of Distributed Computing.' [http://en.wikipedia.org/wiki/Fallacies_of_Distributed_Computing](http://en.wikipedia.org/wiki/Fallacies_of_Distributed_Computing).

[Dolphin] Object Arts. 2000. 'Dolphin Smalltalk; Twisting the Triad.' www.object-arts.com/downloads/papers/TwistingTheTriad.PDF.

[Erl] Erl, Thomas. 2012. 'SOA Principles: An Introduction to the ServiceOriented Paradigm.'

http://serviceorientation.com/index.php/serviceorientation/index.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000655_44bcba716db59404b9452a911fb1bed4a8b47a3c32dd572eaa3ba6fbb575a0ad.png)

[Evans] Evans, Eric. 2004. Domain-Driven Design: Tackling the Complexity in the Heart of Software. Boston, MA: Addison-Wesley.

[Evans, Ref] Evans, Eric. 2012. 'Domain-Driven Design Reference.' [http://domainlanguage.com/ddd/patterns/DDD_Reference_2011-01-31.pdf](http://domainlanguage.com/ddd/patterns/DDD_Reference_2011-01-31.pdf).

[Evans & Fowler, Spec] Evans, Eric, and Martin Fowler. 2012. 'Specifications.' [http://martinfowler.com/apsupp/spec.pdf](http://martinfowler.com/apsupp/spec.pdf).

[Fairbanks] Fairbanks, George. 2011. Just Enough Software Architecture . Marshall & Brainerd.

[Fowler, Anemic] Fowler, Martin. 2003. 'AnemicDomainModel.' [http://martinfowler.com/bliki/AnemicDomainModel.html](http://martinfowler.com/bliki/AnemicDomainModel.html).

[Fowler, CQS] Fowler, Martin. 2005. 'CommandQuerySeparation.' [http://martinfowler.com/bliki/CommandQuerySeparation.html](http://martinfowler.com/bliki/CommandQuerySeparation.html).

[Fowler, DI] Fowler, Martin. 2004. 'Inversion of Control Containers and the Dependency Injection Pattern.'

[http://martinfowler.com/articles/injection.html](http://martinfowler.com/articles/injection.html).

[Fowler, P of EAA] Fowler, Martin. 2003. Patterns of Enterprise Application Architecture . Boston, MA: Addison-Wesley.

[[Fowler, PM] Fowler, Martin. 2004. 'Presentation Model.'](http://martinfowler.com/eaaDev/PresentationModel.html)

[http://martinfowler.com/eaaDev/PresentationModel.html](http://martinfowler.com/eaaDev/PresentationModel.html).

[Fowler, Self Encap] Fowler, Martin. 2012. 'SelfEncapsulation.' [http://martinfowler.com/bliki/SelfEncapsulation.html](http://martinfowler.com/bliki/SelfEncapsulation.html).

[Fowler, SOA] Fowler, Martin. 2005. 'ServiceOrientedAmbiguity.' [http://martinfowler.com/bliki/ServiceOrientedAmbiguity.html](http://martinfowler.com/bliki/ServiceOrientedAmbiguity.html).

[Freeman et al.] Freeman, Eric, Elisabeth Robson, Bert Bates, and Kathy Sierra. 2004. Head First Design Patterns . Sebastopol, CA: O'Reilly Media.

[Gamma et al.] Gamma, Erich, Richard Helm, Ralph Johnson, and John Vlissides. 1994. Design Patterns . Reading, MA: Addison-Wesley.

[Garcia-Molina & Salem] Garcia-Molina, Hector, and Kenneth Salem. 1987. 'Sagas.' ACM, Department of Computer Science, Princeton University, Prince ton, NJ.

www.amundsen.com/downloads/sagas.pdf.

[[GemFire Functions] 2012. VMware vFabric 5 Documentation Center. http://pubs.vmware.com/vfabric5/index.jsp?topic=/com.vmware.vfabric .gemfire.6.6/developing/function_exec/chapter_overview.html.](http://pubs.vmware.com/vfabric5/index.jsp?topic=/com.vmware.vfabric.gemfire.6.6/developing/function_exec/chapter_overview.html)

[Gson] 2012. A Java JSON library hosted on Google Code. [http://code.google.com/p/google-gson/](http://code.google.com/p/google-gson/).

[Helland] Helland, Pat. 2007. 'Life beyond Distributed Transactions: An Apostate's Opinion.' Third Biennial Conference on Innovative DataSystems Research (CIDR), January 7-10, Asilomar, CA.

www.ics.uci.edu/~cs223/papers/cidr07p15.pdf.

[Hohpe & Woolf] Hohpe, Gregor, and Bobby Woolf. 2004. Enterprise Integration Patterns: Designing, Building, and Deploying Messaging Systems . Boston, MA: Addison-Wesley.

[Inductive UI] 2001. Microsoft Inductive User Interface Guidelines. [http://msdn.microsoft.com/en-us/library/ms997506.aspx](http://msdn.microsoft.com/en-us/library/ms997506.aspx).

[Jezequel et al.] Jezequel, Jean-Marc, Michael Train, and Christine Mingins. 2000. Design Patterns and Contract. Reading, MA: Addison-Wesley.

[Keith & Stafford] Keith, Michael, and Randy Stafford. 2008. 'Exposing the ORM Cache.' ACM , May 1.

[http://queue.acm.org/detail.cfm?id=1394141](http://queue.acm.org/detail.cfm?id=1394141).

[Liskov] Liskov, Barbara. 1987. Conference Keynote: 'Data Abstraction and Hierarchy.' [http://en.wikipedia.org/wiki/Liskov_substitution_principle](http://en.wikipedia.org/wiki/Liskov_substitution_principle). 'The Liskov Substitution Principle.'

[www.objectmentor.com/resources/articles/lsp.pdf](https://www.objectmentor.com/resources/articles/lsp.pdf).

[Martin, DIP] Martin, Robert. 1996. 'The Dependency Inversion Principle.' [www.objectmentor.com/resources/articles/dip.pdf](https://www.objectmentor.com/resources/articles/dip.pdf).

[Martin, SRP] Martin, Robert. 2012. 'SRP: The Single Responsibility Principle.' www.objectmentor.com/resources/articles/srp.pdf.

[[MassTransit] Patterson, Chris. 2008. 'Managing Long-Lived Transactions with MassTransit.Saga.'](http://lostechies.com/chrispatterson/2008/08/29/managing-long-lived-transactions-with-masstransit-saga/)

[http://lostechies.com/chrispatterson/2008/08/29/managing-long-livedtransactions-with-masstransit-saga/](http://lostechies.com/chrispatterson/2008/08/29/managing-long-livedtransactions-with-masstransit-saga/).

[[MSDN Assemblies] 2012.](http://msdn.microsoft.com/en-us/library/51ket42z%28v=vs.71%29.aspx)

[http://msdn.microsoft.com/en-us/library/51ket42z%28v=vs.71%29.aspx](http://msdn.microsoft.com/en-us/library/51ket42z%28v=vs.71%29.aspx).

[Nilsson] Nilsson, Jimmy. 2006. Applying Domain-Driven Design and Patterns: With Examples in C# and .NET. Boston, MA: Addison-Wesley.

[Nijof, CQRS] Nijof, Mark. 2009. 'CQRS à la Greg Young.' http://cre8ivethought.com/blog/2009/11/12/cqrs--la-greg-young.

[[NServiceBus] 2012.](http://www.nservicebus.com/)

[www.nservicebus.com/](https://www.nservicebus.com/).

[Öberg] Öberg, Rickard. 2012. 'What Is Qi4j™?' http://qi4j.org/.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000656_d1a45bebf52125d042db60a906b5c7582d1dcaf27d88eb93c8b389f46d524437.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000657_a78bb5b47de16f21577abcd59c759edd7137786af64974b026fe11d1f0fe0f8a.png)

[Parastatidis et al., RiP] Webber, Jim, Savas Parastatidis, and Ian Robinson. 2011. REST in Practice . Sebastopol, CA: O'Reilly Media.

[[PragProg, TDA] The Pragmatic Programmer. 'Tell, Don't Ask.'](http://pragprog.com/articles/tell-dont-ask)

[http://pragprog.com/articles/tell-dont-ask](http://pragprog.com/articles/tell-dont-ask).

[Quartz] 2012. Terracotta Quartz Scheduler. [http://terracotta.org/products/quartz-scheduler](http://terracotta.org/products/quartz-scheduler).

[Seovi þ ] Seovi þ , Aleksandar, Mark Falco, and Patrick Peralta. 2010. Oracle Coherence 3.5: Creating Internet-Scale Applications Using Oracle's High-Performance Data Grid . Birmingham, England: Packt Publishing.

[[SOA Manifesto] 2009. SOA Manifesto.](http://www.soa-manifesto.org/)

www.soa-manifesto.org/.

[[Sutherland] Sutherland, Jeff. 2010. 'Story Points: Why Are They Better than Hours?'](http://scrum.jeffsutherland.com/2010/04/story-points-why-are-they-better-than.html)

[http://scrum.jeffsutherland.com/2010/04/story-points-why-are-they-betterthan.html](http://scrum.jeffsutherland.com/2010/04/story-points-why-are-they-betterthan.html).

[Tilkov, Manifesto] Tilkov, Stefan. 2009. 'Comments on the SOA Manifesto.' [www.innoq.com/blog/st/2009/10/comments_on_the_soa_manifesto.html](https://www.innoq.com/blog/st/2009/10/comments_on_the_soa_manifesto.html).

[Tilkov, RESTful Doubts] Tilkov, Stefan. 2012. 'Addressing Doubts about REST.' [www.infoq.com/articles/tilkov-rest-doubts](https://www.infoq.com/articles/tilkov-rest-doubts).

[Vernon, DDR] Vernon, Vaughn. n.d. 'Architecture and Domain-Driven Design.' [http://vaughnvernon.co/?page_id=38](http://vaughnvernon.co/?page_id=38).

[Vernon, DPO] Vernon, Vaughn. n.d. 'Architecture and Domain-Driven Design.' [http://vaughnvernon.co/?page_id=40](http://vaughnvernon.co/?page_id=40).

[Vernon, RESTful DDD] Vernon, Vaughn. 2010. 'RESTful SOA or DomainDriven Design-A Compromise?' QCon SF 2010. www.infoq.com/presentations/RESTful-SOA-DDD.

[[Webber, REST & DDD] Webber, Jim. 'REST and DDD.'](http://skillsmatter.com/podcast/design-architecture/rest-and-ddd)

[http://skillsmatter.com/podcast/design-architecture/rest-and-ddd](http://skillsmatter.com/podcast/design-architecture/rest-and-ddd).

[Wiegers] Wiegers, Karl E. 2012. 'First Things First: Prioritizing Requirements.'

[www.processimpact.com/articles/prioritizing.html](https://www.processimpact.com/articles/prioritizing.html).

[Wikipedia, CQS] 2012. 'Command-Query Separation.' http://en.wikipedia.org/wiki/Command-query_separation.

[[Wikipedia, EDA] 2012. 'Event-Driven Architecture.'](http://en.wikipedia.org/wiki/Event-driven_architecture)

[http://en.wikipedia.org/wiki/Event-driven_architecture](http://en.wikipedia.org/wiki/Event-driven_architecture).

[Young, ES] Young, Greg. 2010. 'Why Use Event Sourcing?' [http://codebetter.com/gregyoung/2010/02/20/why-use-event-sourcing/](http://codebetter.com/gregyoung/2010/02/20/why-use-event-sourcing/).

## Index

## A

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000658_9800c9ebb19ee7dd1c5c09ae76d0abbcadd88cb22700ebabee728c038eac96dd.png)

| Abstract classes, in modules, 338<br><br>Abstract Factory pattern, 389<br><br>Abstraction, Dependency Inversion Principle and, 123<br><br>Access management, identity and, 91-92<br><br>ACID databases, 521<br><br>ACL. See Anticorruption Layer (ACL)<br><br>Active Record, in Transaction Scripts, 441<br><br>ActiveMQ, as messaging middleware, 303<br><br>Actor Model, 295<br><br>Adapters. See also Hexagonal Architecture<br><br>Domain Services use for integration, 280<br><br>handling client output types, 529-530<br><br>Hexagonal Architecture and, 126-127<br><br>Presentation Model as, 519<br><br>for REST client implementation, 465-466<br><br>Aggregate Root query interface, 516<br><br>Aggregate Stores<br><br>distributed caches of Data Fabrics as, 164<br><br>persistence-oriented repositories and, 418<br><br>Aggregate-Oriented Databases, 418<br><br>Aggregates. See also A+ES (Aggregates and Event Sourcing)<br><br>Application Services and, 120-121<br><br>avoiding dependency Injection, 387<br><br>behavioral focus of, 569-570<br><br>Context Maps and, 90<br><br>cost estimates of memory overhead, 372-373<br><br>creating and publishing Events, 287<br><br>decision process in designing, 379-380<br><br>designing, 573<br><br>designing based on usage scenarios, 375-376<br><br>Domain Events with Aggregate characteristics, 294-295<br><br>Event Sourcing and, 160-162, 539<br><br>eventual consistency, 364-367, 376-378<br><br>executives and trackers merged in, 156<br><br>factories on Aggregate Root, 391-392<br><br>global transactions as reason to break design rules, 369<br><br>implementing, 380 | information hiding (Law of Demeter and Tell, Don't Ask), 382-384<br><br>invariant determination in creating clusters, 353-355<br><br>lack of technical mechanisms as reason to break design rules, 368-369<br><br>local identity of Entities and, 177<br><br>mediators publishing internal state of, 514-515<br><br>memory consumption and, 374-375<br><br>model navigation and, 362-363<br><br>motivations for Factory use, 389<br><br>as object collections, 203<br><br>optimistic concurrency, 385-387<br><br>organizing into large clusters, 349-351<br><br>organizing into smaller units, 351-353<br><br>overview of, 347-348<br><br>placing in repository, 401<br><br>query performance as reason to break design rules, 369-370<br><br>querying repositories and, 138<br><br>references between, 359-362<br><br>removing from repository, 409<br><br>rendering Data Transfer Objects, 513-514<br><br>rendering Domain Payload Objects, 515-516<br><br>rendering properties of multiple instances, 512-513<br><br>rethinking design, 370-372<br><br>review, 388<br><br>Root Entity and, 380-382<br><br>scalability and distribution of, 363-364<br><br>in Scrum Core Domain, 348-349<br><br>single-aggregate-instance-in-single- transaction rule of thumb, 302<br><br>size of Bounded Contexts and, 68<br><br>small Aggregate design, 355-358<br><br>snapshots of, 559-561<br><br>as Standard Type, 237<br><br>state of, 516-517<br><br>storing in Data Fabrics, 164<br><br>synchronizing instances in local Bounded Context, 287 |
| --- | --- |



Aggregates (tiếp theo) tactical modeling tools, 29 results of asking whose job it is, 378-379 usage scenarios applied to designing, 373-374 use cases and, 358-359 user interface convenience as reason to break design rules, 367-368 Value Objects preferred over Entities when possible, 382 Aggregates and Event Sourcing (A+ES) advantages of, 539-540 Aggregate design, 573 BLOB persistence, 568-569 Command Handlers, 549-553 concurrency control, 554-558 contract generation and maintenance, 580-581 drawbacks of, 540 event enrichment, 573-575 event immutability, 577 event serializers, 576-577 event sourcing in functional languages, 583 focusing Aggregates on different behavioral aspects, 569-570 implementing event stores, 561-565 inside Application Services, 541-549 lambda syntax, 553-554 overview of, 539 performance issues, 558-561 Read Model Projections, 570-572 relational persistence, 565-567 structural freedom with, 558 tools and patterns supporting, 576 unit tests and specifications, 582-583 Value Objects and, 577-580 Agile Manifesto, 82 Agile modeling benefits of DDD, 28 design and, 55 Agile Project Management (APM), 177 Agile Project Management Context calculation process from, 277 Context Maps and, 104 as Core Domain, 98 integrating with Collaboration Context, 107-110 integrating with Identity and Access Context, 104-107 modeling Domain Event from, 288-289 modules, 340-343 overview of, 82-84

ProjectOvation as example of, 92 Value Objects and, 239 Ajax Push (Comet), 147 Akka, as messaging middleware, 303 Anemia, 14-16 Anemia-induced memory loss, 16-20 Anemic Domain Model avoiding, 426 causes of, 14-15 determining health of Domain Model and, 13 DTOs mimicking, 532 overuse of services resulting in, 268 overview of, 13 presence of anemia everywhere, 15-16 what anemia does to your model, 16-17 Anticorruption Layer (ACL) Bounded Context relationships, 93-94 built-in, 532 defined, 101 implementing, 469 implementing REST clients and, 463-469 synchronizing team members with identities and roles, 340-341 APIs (application programming interfaces) creating products, 482-483 integration basics and, 450-451 opening services and, 510 APM (Agile Project Management), 177. See also Agile Project Management Context Application Layer composing multiple Bounded Contexts and, 531-532 tạo và đặt tên các module cho các thành phần phi-model, 343-344 DIP (Dependency Inversion Principle) and, 124 in Layers Architecture, 119-121 managing transactions in, 433-434 Application programming interfaces. See APIs (application programming interfaces) Application Services, 68 controlling access and use of Aggregates, 541-549 decoupling service output, 528-530 delegation of, 461-462 Domain Services compared with, 267 enterprise component containers, 534-537 example, 522-528 Hexagonal Architecture and, 126-128

infrastructure and, 509, 532-534

in Layers Architecture, 120-121

message handler, 293

overview of, 521

passing commands to, 550

performing business operations, 545

reasons for not wanting business logic in,
279-280

registering subscribers to Domain Events, 300-302

transactional service in multipleAggregate design, 352-353

Applications

Bounded Contexts and, 66-68 composing multiple Bounded Contexts,
531-532

dealing with multiple, disparate clients, 517-518

defined, 510

enterprise component containers, 534-537

generating identity of Entities, 175-178

infrastructure and, 532-534

mediators, 514-515

overview of, 509-511

rendering Aggregates, 515-516

rendering domain objects, 512-513

rendering DTOs, 513-514

rendition adapters and user edit handling, 518-521

representing state of Aggregate instances, 516-517

review, 534-537

task management for, 549

use case optimal repository queries, 517

user interface, 512

Architects, benefits of DDD to, 5-6

## Architecture

Application Services and, 521

benefits of Aggregates, 540

Bounded Contexts and architectural issues, 68

Context Maps for, 90

CQRS. See CQRS (Command-Query Responsibility Segregation)

creating and naming modules of nonmodel components, 343-344

data fabric and grid-based distributed computing. See Data fabrics

decision process (in fictitious interview), 115-119

DIP (Dependency Inversion Principle) and, 123-125

event driven. See EDA (event-driven architecture)

Layers Architecture pattern, 119-123 overview of, 113-114

Ports and Adapters. See Hexagonal Architecture

REST. See REST (Representational State Transfer)

review, 168-169

SOA (Service-Oriented Architecture), 130-133

Archived logs

finding notification, 315 publishing NotificationLog what they are, 313
, 319-323

Assertions, design-by-contract approach and, 208

Assessment view, for understanding problem space, 57

Attributes, validating Entities, 208-211

Audit logs, 308

Authentication

deciding where to place technical components, 272-275

example of where to use a Domain Service, 269-271

testing authentication service, 281-284 of users, 198

Autonomous services and systems, Domain Events and, 305-306

## B

Behaviors

essential Entity behaviors, 196-200 focusing Aggregates on different behavioral aspects, 569-570

modeling Domain Events, 291-293 naming object behaviors, 31-32 patching classes with specialized behaviors, 225-226

repositories and, 430-432

Big Ball of Mud

Bounded Contexts, 93-94

collaboration issues and, 76

failure from not using strategic design, 55

interfacing with, 88-89

Binary JSON (BSON), 426

Bitcask model, Riak, 569

BLOB (binary large object) persistence, 568-569

Boundaries

Context Maps and, 90

exchanging information across system
boundaries, 452-458

modules and, 344